# execute apt-get update
exec { 'apt-update':
    command => '/usr/bin/apt-get update'
}

#install mongodb
package { 'mongodb':
    require => Exec['apt-update'],
    ensure  => installed
}

#run mongo
service { 'mongodb':
    ensure  => running,
    require => Package['mongodb']
}

#inastall python

class python {

    package {
      [ "python", "python-setuptools", "python-dev", "python-pip",
        "python-matplotlib", "python-imaging", "python-numpy", "python-scipy",
        "python-software-properties", "idle", "python-qt4", "python-wxgtk2.8" ]:
        ensure => ["installed"],
        require => Exec['apt-update']
    }

    exec {
      "virtualenv":
      command => "/usr/bin/sudo pip install virtualenv",
      require => Package["python-dev", "python-pip"]
    }

}

class pythondev {
    package {
        [ "dpkg-dev", "swig", "python2.7-dev", "libwebkitgtk-dev", "libjpeg-dev", "libtiff4-dev",
        "checkinstall", "ubuntu-restricted-extras", "freeglut3", "freeglut3-dev", "libgtk2.0-dev", "libsdl1.2-dev",
        "libgstreamer-plugins-base0.10-dev", "libwxgtk2.8-dev", "libxml2-dev", "libxslt1-dev", "libssl-dev" ]:
        ensure => ["installed"],
        require => Exec['apt-update']
    }

    exec {
      "SquareMap":
      command => "/usr/bin/sudo pip install SquareMap",
      require => Package["python-dev", "python-pip"]
    }

    exec {
      "RunSnakeRun":
      command => "/usr/bin/sudo pip install RunSnakeRun",
      require => Package["python-dev", "python-pip"]
    }

    exec {
        "w3lib":
        command => "/usr/bin/sudo pip install w3lib",
        require => Package["python-dev", "python-pip"]
    }

    exec {
            "lxml":
            command => "/usr/bin/sudo pip install lxml",
            require => Package["python-dev", "python-pip"]
    }

    exec {
                "cssselect":
                command => "/usr/bin/sudo pip install cssselect",
                require => Package["python-dev", "python-pip"]
        }

    exec {
            "scrapy":
            command => "/usr/bin/sudo pip install scrapy",
            require => Package["python-dev", "python-pip"]
        }
}

class networking {
    package {
      [ "snmp", "tkmib", "curl", "wget" ]:
        ensure => ["installed"],
        require => Exec['apt-update']
    }

}



include python
include pythondev
include networking
