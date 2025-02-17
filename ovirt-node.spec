%global product_family oVirt Node
%global product_release %{version} (0)
%global mgmt_scripts_dir %{_sysconfdir}/node.d
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}


Summary:        The %{product_family} daemons/scripts
Name:           ovirt-node
Version:        2.0.1
Release:        4%{?dist}%{?extra_release}
Source0:        %{name}-%{version}.tar.gz
Patch1:         0001-in-development-Fedoras-have-updates-testing.patch
License:        GPLv2+
Group:          System/Configuration/Other
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:            https://www.ovirt.org/
BuildRequires:  python-setuptools
BuildRequires:  automake autoconf
Requires(post):  /sbin/chkconfig
Requires(preun): /sbin/chkconfig
%if 0%{?fedora}
Requires:       python-augeas
Requires:       glusterfs-client >= 2.0.1
Requires:       anyterm
Requires:       python-IPy
%endif
Requires:       libvirt >= 0.9.2
Requires:       augeas >= 0.3.5
Requires:       udev >= 147-2.34
Requires:       wget
Requires:       cyrus-sasl-gssapi cyrus-sasl >= 2.1.22
Requires:       iscsi-initiator-utils
Requires:       ntp
Requires:       nfs-utils
Requires:       krb5-workstation
Requires:       bash
Requires:       chkconfig
Requires:       bind-utils
Requires:       qemu-img
Requires:       nc
Requires:       grub
Requires:       /usr/sbin/crond
Requires:       newt-python
Requires:       libuser-python >= 0.56.9
Requires:       dbus-python
Requires:       python-gudev
Requires:       PyPAM
Requires:       ethtool
Requires:       cracklib-python
Requires:       dracut
%if 0%{?rhel}
# for applying patches in %post
Requires:       patch
%endif
Requires:       system-release

BuildArch:      noarch

%define app_root %{_datadir}/%{name}

%description
Provides a series of daemons and support utilities for hypervisor distribution.

%package tools
Summary:        Tools for building and running %{product_family} image
Group:          Applications/System
Requires:       pykickstart  >= 1.54
Requires:       livecd-tools >= 020-2

%define tools_root %{_datadir}/ovirt-node-tools

%description tools
This package provides recipe (Kickstart files), client tools,
documentation for building and running an %{product_family} image.
This package is not to be installed on the %{product_family},
however on a development machine to help to build the image.

%prep
%setup -q
%patch1 -p1

%build
aclocal && autoheader && automake --add-missing && autoconf
%configure
make

%install
%{__rm} -rf %{buildroot}
make install DESTDIR=%{buildroot}

# FIXME move all installs into makefile
%{__install} -d -m0755 %{buildroot}%{_initrddir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/cron.hourly
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -d -m0755 %{buildroot}%{mgmt_scripts_dir}
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/cron.d
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/dracut.conf.d

%{__install} -p -m0755 scripts/node-config %{buildroot}%{_sysconfdir}/sysconfig

%{__install} -p -m0755 scripts/ovirt-awake %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-early %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-post %{buildroot}%{_initrddir}
%{__install} -p -m0755 scripts/ovirt-firstboot %{buildroot}%{_initrddir}

%{__install} -p -m0644 logrotate/ovirt-logrotate %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -m0644 logrotate/ovirt-logrotate.conf %{buildroot}%{_sysconfdir}/logrotate.d/ovirt-node
# configure libvirtd upstart job
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/init
%{__install} -p -m0644 libvirtd.upstart %{buildroot}%{_sysconfdir}/init/libvirtd.conf
# load vlan module
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/sysconfig/modules
%{__install} -p -m0755 vlan.modules %{buildroot}%{_sysconfdir}/sysconfig/modules

#dracut module for disk cleanup
%{__install} -d -m0755 %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/check %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/install %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 scripts/ovirt-boot-functions %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0755 dracut/ovirt-cleanup.sh %{buildroot}%{_datadir}/dracut/modules.d/91ovirtnode
%{__install} -p -m0644 dracut/ovirt-dracut.conf %{buildroot}%{_sysconfdir}/dracut.conf.d
%if 0%{?rhel}
# dracut patches for rhel6
%{__install} -p -m0644 dracut/dracut-3d88d27810acc7782618d67a03ff5c0e41494ca4.patch %{buildroot}%{app_root}
%{__install} -p -m0644 dracut/dracut-93724aa28fc20c8b7f0167201d1759b7118ba890.patch %{buildroot}%{app_root}
%endif

# resolv.conf augeas lens
%{__install} -d -m0755 %{buildroot}/usr/share/augeas/lenses
%{__install} -p -m0644 augeas/build.aug %{buildroot}/usr/share/augeas/lenses/build.aug
%{__install} -p -m0644 augeas/resolv.aug %{buildroot}/usr/share/augeas/lenses/resolv.aug
%{__install} -p -m0644 augeas/util.aug %{buildroot}/usr/share/augeas/lenses/util.aug

mkdir -p %{buildroot}/%{_sysconfdir}/default
echo "# File where default configuration is kept" > %{buildroot}/%{_sysconfdir}/default/ovirt

# ovirt-config-boot post-install hooks
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/ovirt-config-boot.d
# default hook for local_boot_trigger
%{__install} -p -m0755 scripts/local_boot_trigger.sh %{buildroot}%{_sysconfdir}/ovirt-config-boot.d

# newt UI
%{__install} -d -m0755 %{buildroot}%{python_sitelib}/ovirt_config_setup
%{__install} -p -m0644 scripts/__init__.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%if 0%{?fedora}
%{__install} -p -m0644 scripts/collectd.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%endif
%if 0%{?rhel}
%{__install} -p -m0644 scripts/rhn.py %{buildroot}%{python_sitelib}/ovirt_config_setup
%endif
%{__install} -d -m0755 %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/__init__.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/storage.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/password.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/install.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/iscsi.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/kdump.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/logging.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/ovirtfunctions.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0644 scripts/network.py %{buildroot}%{python_sitelib}/ovirtnode
%{__install} -p -m0755 scripts/ovirt-config-installer.py %{buildroot}%{_libexecdir}/ovirt-config-installer
%{__install} -p -m0755 scripts/ovirt-config-setup.py %{buildroot}%{_libexecdir}/ovirt-config-setup
%{__install} -p -m0755 scripts/ovirt-admin-shell %{buildroot}%{_libexecdir}
%if 0%{?rhel}
# python-augeas is not in RHEL-6
%{__install} -p -m0644 scripts/augeas.py %{buildroot}%{python_sitelib}
%endif

# ovirt-early vendor hook dir
%{__install} -d -m0755 %{buildroot}%{_sysconfdir}/ovirt-early.d


%clean
%{__rm} -rf %{buildroot}

%post
/sbin/chkconfig --add ovirt-awake
/sbin/chkconfig --add ovirt-early
/sbin/chkconfig --add ovirt-firstboot
/sbin/chkconfig --add ovirt
/sbin/chkconfig --add ovirt-post
# workaround for imgcreate/live.py __copy_efi_files
if [ ! -e /boot/grub/splash.xpm.gz ]; then
  cp %{app_root}/grub-splash.xpm.gz /boot/grub/splash.xpm.gz
fi
%if 0%{?rhel}
# apply dracut fixes not in rhel6
# rhbz#683330
# dracut.git commits rediffed for dracut-004-53.el6
patch -d /usr/share/dracut/ -p0 < %{app_root}/dracut-3d88d27810acc7782618d67a03ff5c0e41494ca4.patch
patch -d /usr/share/dracut/ -p0 < %{app_root}/dracut-93724aa28fc20c8b7f0167201d1759b7118ba890.patch
%endif
#use all hard-coded defaults for multipath
> /etc/multipath.conf
#release info for dracut to pick it up into initramfs
echo "%{product_family} release %{product_release}" > /etc/system-release

%preun
if [ $1 = 0 ] ; then
    /sbin/service ovirt-early stop >/dev/null 2>&1
    /sbin/service ovirt-firstboor stop >/dev/null 2>&1
    /sbin/service ovirt stop >/dev/null 2>&1
    /sbin/service ovirt-post stop >/dev/null 2>&1
    /sbin/chkconfig --del ovirt-awake
    /sbin/chkconfig --del ovirt-early
    /sbin/chkconfig --del ovirt-firstboot
    /sbin/chkconfig --del ovirt
    /sbin/chkconfig --del ovirt-post
fi


%files tools
%defattr(0644,root,root,0755)
%doc README COPYING
%{tools_root}/*.ks
%defattr(0755,root,root,0755)
%{_sbindir}/node-creator


%files
%defattr(-,root,root)
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/default/ovirt

%config(noreplace) %{_sysconfdir}/logrotate.d/ovirt-node
%config(noreplace) %{_sysconfdir}/cron.d/ovirt-logrotate

%{mgmt_scripts_dir}
%{_sysconfdir}/ovirt-config-boot.d
%config(noreplace) %{_sysconfdir}/sysconfig/node-config

%{_sysconfdir}/init/libvirtd.conf

%{_sysconfdir}/sysconfig/modules/vlan.modules

%doc COPYING
# should be ifarch i386
%{app_root}/grub-splash.xpm.gz
# end i386 bits
%{app_root}/syslinux-vesa-splash.jpg
%if 0%{?rhel}
%{app_root}/dracut-3d88d27810acc7782618d67a03ff5c0e41494ca4.patch
%{app_root}/dracut-93724aa28fc20c8b7f0167201d1759b7118ba890.patch
%endif

%{_datadir}/augeas/lenses/build.aug
%{_datadir}/augeas/lenses/resolv.aug
%{_datadir}/augeas/lenses/util.aug
%{_datadir}/dracut/modules.d/91ovirtnode/check
%{_datadir}/dracut/modules.d/91ovirtnode/install
%{_datadir}/dracut/modules.d/91ovirtnode/ovirt-boot-functions
%{_datadir}/dracut/modules.d/91ovirtnode/ovirt-cleanup.sh
%{_sysconfdir}/dracut.conf.d/ovirt-dracut.conf
%{_libexecdir}/ovirt-config-boot
%{_libexecdir}/ovirt-config-boot-wrapper
%{_libexecdir}/ovirt-config-hostname
%{_libexecdir}/ovirt-config-iscsi
%{_libexecdir}/ovirt-config-kdump
%{_libexecdir}/ovirt-config-logging
%{_libexecdir}/ovirt-config-networking
%{_libexecdir}/ovirt-config-password
%{_libexecdir}/ovirt-config-rhn
%{_libexecdir}/ovirt-config-snmp
%{_libexecdir}/ovirt-config-storage
%{_libexecdir}/ovirt-config-uninstall
%{_libexecdir}/ovirt-config-view-logs
%{_libexecdir}/ovirt-functions
%{_libexecdir}/ovirt-boot-functions
%{_libexecdir}/ovirt-process-config
%{_libexecdir}/ovirt-rpmquery
%{_libexecdir}/ovirt-config-installer
%{_libexecdir}/ovirt-config-setup
%{_libexecdir}/ovirt-admin-shell
%{_sbindir}/persist
%{_sbindir}/unpersist
%{python_sitelib}/ovirt_config_setup
%{python_sitelib}/ovirtnode
%if 0%{?rhel}
%{python_sitelib}/augeas*
%endif

%{_initrddir}/ovirt-awake
%{_initrddir}/ovirt-early
%{_initrddir}/ovirt-firstboot
%{_initrddir}/ovirt
%{_initrddir}/ovirt-post
%{_sysconfdir}/ovirt-early.d

