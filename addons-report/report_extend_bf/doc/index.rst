
Install module in S.O. based Linux
----------------------------------

- Red Hat
- Debian
- Fedora
- Mandriva
- Ubuntu
- OpenSUSE
- Others linux distro.

Pre-Installation Requirements
-----------------------------

- **Unoconv**: Convert files to any format that supports LibreOffice. Website: `Unoconv <http://dag.wiee.rs/home-made/unoconv/>`_ example install ubuntu O.S. 


# apt-get install unoconv subversion

**Install py3o.template with python 3 support**

- **py3o.template**: An easy solution to design reports using OpenOffice, for basic templating (odt->odt and ods->ods only) 

Ref: `py3o.template install <https://bitbucket.org/faide/py3o.template>`_

Preferably install in this order:

py3o.template is python3 ready. But, yes there is a but... alas!, you'll need to install a trunk version of Genshi.

pip3 install py3o.template==0.9.12

Uninstall genshi
 
pip3 uninstall genshi

And we reinstall genshi

svn checkout https://svn.edgewall.org/repos/genshi/trunk genshi_trunk

cd genshi_trunk

python3 setup.py build

python3 setup.py install

Or see example script `Vagrant install <https://github.com/dperaltab/odoo-vagrant/tree/11.0_report_extend_bf>`_


Supported output format combinations (Template -> Output):

- odt -> odt (default)
- odt -> pdf
- odt -> doc
- odt -> docx
- odt -> pds
- rtf -> rtf

Note
----
If the program unoconv default output will show in ODT format regardless of the output field you selected in the report is not installed.

- Fully Supports Odoo Version 11.0 Community

