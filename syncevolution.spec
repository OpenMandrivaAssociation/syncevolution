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
Release:       2
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
# evolution-data-server 3.59 renamed EVCardFormat to EVCardVersion.
Patch6:        syncevolution-2.0.0-eds-3.59.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool-base
BuildRequires:	slibtool
BuildRequires:	make
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
# autoupdate rewrites AC_LIBTOOL_DLOPEN into _LT_SET_OPTION, which slibtool
# does not define, so configure stops on that token.
sed -i '/^AC_LIBTOOL_DLOPEN$/d; s/^AC_PROG_LIBTOOL$/LT_INIT([dlopen])/' configure.ac
# C23 makes bool a keyword, so the SDK cannot typedef it.
sed -i 's/#if !defined(__cplusplus) && !defined(__OBJC__)/#if !defined(__cplusplus) \&\& !defined(__OBJC__) \&\& (!defined(__STDC_VERSION__) || __STDC_VERSION__ < 202311L)/' \
	src/synthesis/src/sysync_SDK/Sources/sync_include.h
# slibtool prefixes ../ onto an absolute .la, then the link runs from
# the top directory and cannot open the file. Keep the .la names as
# make dependencies and pass the built archive and shared libraries.
python << 'PY'
from pathlib import Path
p = Path("configure.ac")
text = p.read_text()
old = """    SYNTHESIS_DEP=$SYNTHESIS_LIBS

    # for linking client-test
    SYNTHESIS_ENGINE=\"$SYNTHESIS_SUBDIR/src/libsynthesis.la\"
"""
new = """    SYNTHESIS_DEP=$SYNTHESIS_LIBS
    SYNTHESIS_LIBS=`printf '%s\\n' \"$SYNTHESIS_LIBS\" | sed \\
        -e \"s|$SYNTHESIS_SUBDIR/src/libsynthesissdk.la|$SYNTHESIS_SUBDIR/src/.libs/libsynthesissdk.a|g\" \\
        -e \"s|$SYNTHESIS_SUBDIR/src/libsmltk.la|-L$SYNTHESIS_SUBDIR/src/.libs -lsmltk|g\" \\
        -e \"s|$SYNTHESIS_SUBDIR/src/libsynthesis.la|-L$SYNTHESIS_SUBDIR/src/.libs -lsynthesis|g\"`
    SYNTHESIS_ENGINE=\"-L$SYNTHESIS_SUBDIR/src/.libs -lsynthesis\"
"""
if old not in text:
    raise SystemExit("configure.ac synthesis link block not found")
p.write_text(text.replace(old, new, 1))
PY

%build
autoupdate
intltoolize --automake --copy --force
autoreconf -fiv
# slibtoolize drops its m4 after aclocal, so LT_INIT stays unexpanded.
aclocal -I m4 -I m4-repo
autoconf
autoheader || :
automake --add-missing --copy --force-missing

pushd src/synthesis
autoupdate
autoreconf -fi
aclocal
autoconf
autoheader || :
automake --add-missing --copy --force-missing || :
./autogen.sh
popd

export CC=gcc
export CXX=g++

%configure --enable-libcurl --disable-libsoup --enable-dbus-service --enable-shared \
    --disable-static --enable-gtk=3 --enable-gui --enable-dav --enable-bluetooth \
    --disable-akonadi --enable-signon=no --enable-goa=no \
    --with-expat=system

# slibtool does not leave a libtool script behind. GNU libtool still does.
if [ -f libtool ]; then
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g
        s|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
fi

# Synthesis is built by its own GNU libtool. slibtool will not link those
# .la archives unless each one has a .so.slibtool.deps or .a.slibtool.deps record.
if [ -f src/build-synthesis/libtool ]; then
mv src/build-synthesis/libtool src/build-synthesis/libtool.gnu
cat > src/build-synthesis/libtool << 'EOF'
#!/bin/sh
here=$(dirname "$0")
"$here/libtool.gnu" "$@"
status=$?
if [ "$status" -eq 0 ]; then
  for arg in "$@"; do
    case $arg in
      *.la)
        base=${arg##*/}
        base=${base%.la}
        parent=${arg%/*}
        [ "$parent" = "$arg" ] && parent=.
        write_deps() {
          dest=$1
          if [ -e "$dest" ]; then
            return
          fi
          sed -n "s/.*dependency_libs='\([^']*\)'.*/\1/p" "$arg" |
            tr ' ' '\n' |
            grep -E '^(-l|-L|-Wl,)' > "$dest" || :
          # A newline-only record is one empty linker argument
          # ("cannot find :"). A zero-length file adds nothing.
          if [ ! -s "$dest" ]; then
            : > "$dest"
          fi
        }
        # Shared libs are recorded as NAME.so.slibtool.deps. Static libs
        # use NAME.a.slibtool.deps. libsmltk is shared-only, so the .a
        # record is never created and slibtool then demands .a.disabled.
        if [ -e "$parent/.libs/$base.so" ]; then
          write_deps "$parent/.libs/$base.so.slibtool.deps"
        fi
        if [ -f "$parent/.libs/$base.a" ]; then
          write_deps "$parent/.libs/$base.a.slibtool.deps"
        fi
        ;;
    esac
  done
fi
exit "$status"
EOF
chmod +x src/build-synthesis/libtool
fi

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


