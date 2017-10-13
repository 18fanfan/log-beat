#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from config_loader import config
from util import Util as ut
import logging, zipfile
from simple_cipher import AES_TOTP


# logging
logger = logging.getLogger(config.log_root)
logger.setLevel(getattr(logging, config.severity))
fh = logging.FileHandler(config.log_path)
formatter = logging.Formatter("%(asctime)s - %(pathname)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
ut.logger = logger

cipher = AES_TOTP()
# pre cleanup

def zip_extraction (fd, log_base):
    try:
        with zipfile.ZipFile(fd, 'r') as z:
            for info in z.infolist():
                logger.info("extract log:[%s%s]" % (log_base, info.filename))
                z.extract(info, log_base)
    except zipfile.BadZipfile as e:
        logger.error("bad zip file: %s" % e)  
    


def data_landing(company_name, host):
    company_log_base = "%s%s/" % (config.unpack_dest_dir, company_name)
    ut.mkdir_p(company_log_base)
    log_file_name = "%s%s.zip.%s" % (config.packer_prefix, ut.get_today_date(), config.cipher_ext)
    request_path = "%s%s" % (config.download_path, log_file_name)
    enc_fd = ut.fetch_log(host, company_name, request_path)

    if enc_fd is not None:
        #decryption. After decryption, enc_fd is closed
        zip_fd = ut.decrypt_in_mm(enc_fd, cipher)
        zip_extraction(zip_fd, company_log_base)


if __name__ == '__main__':
    ut.remove(config.unpack_dest_dir)
    ut.mkdir_p(config.unpack_dest_dir)

    for company in config.Company.items():
        data_landing(*company)

# multiple process?
# routine job (after 06:40)
# ELK integration, add appliance field 
# firewall setup
