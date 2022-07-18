
FROM python:3.8-buster

# set author
MAINTAINER Lain Pavot <lain.pavot@inrae.fr>

# set encoding
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV R_BASE_VERSION 4.0.3

ENV PLANEMO_VENV_LOCATION /planemo-venv
ENV CONDA /tmp/conda

RUN \
        apt-get update                                                                                         \
    &&  apt-get install -y --no-install-recommends                                                             \
        ed                                                                                                     \
        less                                                                                                   \
        locales                                                                                                \
        vim-tiny                                                                                               \
        wget                                                                                                   \
        ca-certificates                                                                                        \
        fonts-texgyre                                                                                          \
    &&  echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen                                                            \
    &&  locale-gen en_US.utf8                                                                                  \
    &&  /usr/sbin/update-locale LANG=en_US.UTF-8                                                               \
    &&  echo "deb http://http.debian.net/debian buster main" > /etc/apt/sources.list.d/debian-unstable.list    \
    &&  echo 'APT::Default-Release "buster";' > /etc/apt/apt.conf.d/default                                    \
    &&  echo 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/90local-no-recommends                    \
    &&  apt-get update                                                                                         \
    &&  apt-get upgrade -y                                                                                     \
    &&  apt-get install -y --no-install-recommends                                                             \
        git                                                                                                    \
        littler                                                                                                \
        libhdf5-dev                                                                                            \
        r-cran-littler                                                                                         \
        r-base                                                                                                 \
        r-base-dev                                                                                             \
        r-recommended                                                                                          \
        python-virtualenv                                                                                      \
    &&  pip install virtualenv                                                                                 \
    &&  python -m virtualenv "$PLANEMO_VENV_LOCATION"                                                          \
    &&  . "$PLANEMO_VENV_LOCATION"/bin/activate                                                                \
    &&  pip install --upgrade pip setuptools                                                                   \
    &&  pip install planemo numpy                                                                              \
    &&  planemo conda_init --conda_prefix "$CONDA"                                                             \
    &&  apt-get clean autoclean                                                                                \
    &&  apt-get autoremove --yes                                                                               \
    &&  rm -rf /var/lib/{apt,dpkg,cache,log}/                                                                  \
    &&  rm -rf /usr/bin/X11                                                                                    \
    &&  rm -rf /tmp/*                                                                                          ;

CMD []

