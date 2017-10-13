#!/usr/bin/python
import time, os, json, logging, gzip
from simple_cipher import AES_TOTP
from config_loader import config
from util import Util as ut
from zipfile import ZipFile, ZIP_DEFLATED

# logging setup
ut.remove(config.log_path)

logger = logging.getLogger(config.log_root)
logger.setLevel(getattr(logging, config.severity))
fh = logging.FileHandler(config.log_path)
formatter = logging.Formatter("%(asctime)s - %(pathname)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
ut.logger = logger

def add_log_file(zip_path, log_path):
    print 'add log to zip file'
    with ZipFile(zip_path, 'a') as zd:
        zd.write(log_path, arcname=os.path.basename(log_path))


def remove_previous_logpack():
    for filename in os.listdir(config.cipher_dest_dir):
        if filename.startswith(config.packer_prefix):
            target = "%s%s" % (config.cipher_dest_dir, filename)
            ut.remove(target)
            logger.info('remove file: %s' % (target))

def organize_logs():
    log_path = map(ut.convert_to_path, config.log_list)
    ut.mkdir_p(config.ha_landing_base)

    if ut.is_ha():
        for path in log_path:
            ut.org_peer_logs(path, config.ha_landing_base)
    
    for path in log_path:
        ut.org_local_logs(path, config.ha_landing_base)

 
def logpack_to_zip():
    zip_path = "%s%s%s.zip" % (config.packer_dest_dir, config.packer_prefix, ut.get_today_date())

    print 'packing log'
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zd:
        for cwd, dirs, files in os.walk(config.ha_landing_base):
            for filename in files:
                target_log = "%s/%s" % (cwd, filename)
                name = target_log.replace(config.ha_landing_base, '')
                print target_log
                zd.write(target_log, arcname = name)
                logger.info('add log to zip: %s' % target_log)

    ut.remove(config.ha_landing_base)
    logger.info('remove log base: %s' % config.ha_landing_base)
    return zip_path


def encryption(src_path):
    # Using default counter_base and hotp_secret
    cipher = AES_TOTP()
    file_name = os.path.basename(src_path)
    dest_path = "%s%s.%s" % (config.cipher_dest_dir, file_name, config.cipher_ext)
    logger.info('file encryption: %s --> %s' % (src_path, dest_path))
    add_log_file(src_path, config.log_path)
    print 'do encryption'
    cipher.encrypt_file(src_path, dest_path)
    ut.remove(src_path)


remove_previous_logpack()
organize_logs()        
zip_path = logpack_to_zip()
encryption(zip_path)

print 'DONE'
