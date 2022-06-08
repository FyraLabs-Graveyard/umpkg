%undefine _disable_source_fetch

Name:           umpkg
Version:        0.3.3
Release:        1%{?dist}
Summary:        Summary here
URL:            url.to.official.website.org
Source0:        https://github.com/Ultramarine-Linux/umpkg/archive/refs/tags/%{version}.tar.gz
License:        MIT
BuildRequires:  python3-devel
Requires:       mock
Group:          Applications/Internet
BuildArch:      noarch
%description
This is a very long description of umpkg.

%prep
%autosetup -n umpkg-%{version}

%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files umpkg

%files -f %{pyproject_files}
%{_bindir}/umpkg

%changelog
* Sat May 28 2022 Cappy Ishihara <cappy@cappuchino.xyz> - 0.3.1-1.um36
- Initial Rewrite
