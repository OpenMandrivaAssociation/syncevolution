%define _disable_lto 1

%define _libexecdir /usr/libexec
%define _disable_ld_no_undefined 1
%define _disable_rebuild_configure 1

%define gdbussyncevo_major 0
%define gdbussyncevo_libname %mklibname gdbussyncevo %gdbussyncevo_major
%define smltk_major 0
%define smltk_libname %mklibname smltk %smltk_major
%define syncevodbus_major 0
%define syncevodbus_libname %mklibname syncevo-dbus %syncevodbus_major
%define syncevolution_major 0
%define syncevolution_libname %mklibname syncevolution %syncevolution_major
%define synthesis_major 0
%define synthesis_libname %mklibname synthesis %synthesis_major

%define develname %mklibname %name -d

Summary:       SyncML client for evolution
Name:          syncevolution
Version:       2.0.0
Release:       1
License:       LGPLv2+
Group:         Networking/Remote access 
URL:           https://syncevolution.org/
Source0:       http://downloads.syncevolution.org/%{name}/sources/%{name}-%{version}.tar.gz
Source100:     syncevolution.rpmlintrc
Patch1:	       syncevolution-1.5.1-libical2.patch
Patch2:        syncevolution-1.5.3-autoconf-2.71.patch
Patch3:        003-pcre2.patch
Patch4:        004-cpp-curl.patch
Patch5:        syncevolution-2.0.0-clang.patch
BuildRequires: pkgconfig(bluez)
BuildRequires: boost-devel
BuildRequires: pkgconfig(cppunit)
BuildRequires: pkgconfig(dbus-glib-1)
BuildRequires: pkgconfig(libedataserver-1.2)
BuildRequires: pkgconfig(expat)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(libsecret-1)
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(libcurl)
BuildRequires: pkgconfig(libical)
BuildRequires: pkgconfig(libnotify)
BuildRequires: pkgconfig(neon)
BuildRequires: pkgconfig(libpcre2-8)
BuildRequires: pkgconfig(unique-1.0)
BuildRequires: pkgconfig(openobex)
BuildRequires: pkgconfig(libebook-1.2)
BuildRequires: desktop-file-utils
#BuildRequires: libtlen-devel
BuildRequires: pkgconfig(libecal-2.0)
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: libtool
BuildRequires: xsltproc
BuildRequires: python-docutils
BuildRequires: python-pygments
BuildRequires: python-distribute
BuildRequires: pkgconfig(python)
BuildRequires: gcc-c++
BuildRequires: gcc
BuildRequires: gcc-cpp

Requires: python3dist(twisted)
Requires: %{name}-backends

%description
syncevolution is designed to provide a SyncML client that can
connect to and sync with various SyncML-based servers

%package backends
Group:          System/Libraries
Summary:        %{name} backend plugins

%description backends
This package contains the backend plugins for %{name}.

%package -n %{gdbussyncevo_libname}
Group:          System/Libraries
Summary:        Gdbussyncevo library

%description -n %{gdbussyncevo_libname}
This package contains the gdbussyncevo library.

%package -n %{smltk_libname}
Group:          System/Libraries
Summary:        Smltk library

%description -n %{smltk_libname}
This package contains the smltk library.

%package -n %{syncevodbus_libname}
Group:          System/Libraries
Summary:        Syncevo-dbus library

%description -n %{syncevodbus_libname}
This package contains the syncevo-dbus library.

%package -n %{syncevolution_libname}
Group:          System/Libraries
Summary:        Syncevolution library

%description -n %{syncevolution_libname}
This package contains the syncevolution library.

%package -n %{synthesis_libname}
Group:          System/Libraries
Summary:        Synthesis library

%description -n %{synthesis_libname}
This package contains the synthesis library.

%package -n %{develname}
Summary: Development package for %{name}
Group: Development/C
Requires: %{name} = %{EVRD}

%description -n %{develname}
Files for development with %{name}.

%package gtk
Summary: GTK+ GUI for %{name}
Group: Networking/Remote access 
Requires: %{name} = %{EVRD}

%description gtk
GTK+ GUI for use with %{name}.

%package perl
Summary: Perl utils for %{name}
Group: Development/Perl
Requires: %{name} = %{EVRD}

%description perl
Perl utils for use with %{name}.

%prep
%autosetup -p1

# use the ac macros in Makefile.am
sed -i '/^ACLOCAL_AMFLAGS/{ /m4-repo/!s/$/ -I m4-repo/ }' Makefile*.am

%build
autoupdate
intltoolize --automake --copy --force
autoreconf -fiv

pushd src/synthesis
autoupdate
autoreconf -fi
./autogen.sh
popd

export CC=gcc
export CXX=g++

%configure --enable-libcurl --disable-libsoup --enable-dbus-service --enable-shared \
    --disable-static --enable-gtk=3 --enable-gui --enable-dav --enable-bluetooth \
    --disable-akonadi --enable-signon=no --enable-goa=no \
    --with-expat=system

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g
        s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%make_build V=1
find . -type d -perm 02755 -exec chmod 0755 '{}' \;


%install
%make_install
rm -rf %{buildroot}%{_datadir}/doc

%find_lang %{name}

%files -f %{name}.lang
%doc AUTHORS NEWS README HACKING README.rst
%{_sysconfdir}/xdg/autostart/syncevo-dbus-server.desktop
%{_bindir}/syncevolution
%{_bindir}/syncevo-http-server
%{_bindir}/syncevo-phone-config
%{_bindir}/synclog2html
%{_bindir}/syncevo-webdav-lookup
%{_libexecdir}/syncevo-dbus-helper
%{_libexecdir}/syncevo-dbus-server
%{_libexecdir}/syncevo-dbus-server-startup.sh
%{_libexecdir}/syncevo-local-sync
%{_datadir}/syncevolution
%{_datadir}/dbus-1/services/org.syncevolution.service
%{_userunitdir}/syncevo-dbus-server.service
%{_mandir}/man1/syncevolution.1*
%exclude %{_datadir}/syncevolution/xml/*.pl

%files backends
%doc AUTHORS NEWS README
%dir %{_libdir}/syncevolution
%{_libdir}/syncevolution/backends

%files -n %{gdbussyncevo_libname}
%doc AUTHORS NEWS README
%{_libdir}/libgdbussyncevo.so.%{gdbussyncevo_major}*

%files -n %{smltk_libname}
%doc AUTHORS NEWS README
%{_libdir}/libsmltk.so.%{smltk_major}*

%files -n %{syncevodbus_libname}
%doc AUTHORS NEWS README
%{_libdir}/libsyncevo-dbus.so.%{syncevodbus_major}*

%files -n %{syncevolution_libname}
%doc AUTHORS NEWS README
%{_libdir}/libsyncevolution.so.%{syncevolution_major}*

%files -n %{synthesis_libname}
%doc AUTHORS NEWS README
%{_libdir}/libsynthesis.so.%{synthesis_major}*

%files -n %{develname}
%doc AUTHORS NEWS README
%{_includedir}/syncevo
%{_includedir}/syncevo-dbus
%{_includedir}/synthesis
%{_libdir}/pkgconfig/s*.pc
%{_libdir}/*.so
%{_libdir}/*.a

%files gtk
%doc AUTHORS NEWS README
%{_bindir}/sync-ui
%{_datadir}/applications/sync.desktop
%{_datadir}/icons/hicolor/48x48/apps/sync.png

%files perl
%doc AUTHORS NEWS README
%{_bindir}/synccompare
%{_datadir}/syncevolution/xml/*.pl


