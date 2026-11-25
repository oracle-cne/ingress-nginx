
%global debug_package %{nil}
%global registry container-registry.oracle.com/olcne
%global _name ingress-nginx

%ifarch %{arm} arm64 aarch64
%global custom_arch arm64
%else
%global custom_arch amd64
%endif

Name:    %{_name}-container-image
Version: 1.15.1
Release: 2%{?dist}
Summary: High performance web server
License: 2-clause BSD-like license
URL:     https://github.com/kubernetes/ingress-nginx
Vendor:  Oracle America
Source0: %{_name}-%{version}.tar.bz2
BuildRequires: podman
BuildRequires: golang

Patch0: Makefile.patch
Patch1: build.sh.patch
Patch2: Dockerfile.patch
Patch3: Dockerfile_controller.patch
Patch4: nginx.tmpl.patch
Patch5: run-in-docker.sh.patch

%description
%{summary}

%prep
%setup -q -n %{_name}-%{version}
%patch0
%patch1
%patch2
%patch3
%patch4
%patch5

%build
mkdir -p ${HOME}/.kube
export GO111MODULE=on
export RUNTIME=podman
export PKG=k8s.io/ingress-nginx
export TAG=v%{version}
export COMMIT_SHA=$(git rev-parse --short HEAD)
export REPO_INFO=nginx-ingress
export TARGETS_DIR=rootfs/bin/%{custom_arch}
export CGO_ENABLED=0
export GOOS=linux

cp buildrpm/oracle*.repo images/nginx/rootfs/
chmod +x ./build-images.sh
bash -x ./build-images.sh %{version}-1 %{custom_arch}

%install
%__install -D -m 644 ingress-nginx-controller.tar %{buildroot}/usr/local/share/olcne/ingress-nginx-controller.tar
%__install -D -m 644 kube-webhook-certgen.tar %{buildroot}/usr/local/share/olcne/kube-webhook-certgen.tar
%__install -D -m 644 custom-error-pages.tar %{buildroot}/usr/local/share/olcne/custom-error-pages.tar

%files
%license LICENSE
/usr/local/share/olcne/ingress-nginx-controller.tar
/usr/local/share/olcne/kube-webhook-certgen.tar
/usr/local/share/olcne/custom-error-pages.tar

%changelog
* Fri Nov 20 2026 Daniel Krasinski <daniel.krasinski@oracle.com> - 1.15.1-2
- Apply patches for CVE-2026-123634, CVE-2026-113425, CVE-2026-123007, and CVE-2026-123633
- Bump go.mod dependencies

* Fri Mar 20 2026 Oracle Cloud Native Environment Authors <noreply@oracle.com> - 1.15.1-1
- Added Oracle Specific Build Files for ingress-nginx-container-image
