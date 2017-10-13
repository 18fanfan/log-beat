import time, shutil, os, ssl, httplib, io
from peercontrol import peercontrol

class Util(object):
    # class variable
    pc = peercontrol()

    @classmethod
    def get_today_date(cls):
        return time.strftime("%Y%m%d", time.localtime()) 


    @classmethod
    def convert_to_path(cls, log):
        return "%s-%s" % (log, cls.get_today_date())


    @classmethod
    def is_ha(cls):
        status, msg = cls.pc.execute_cmd_in_peer('whoami') 
        if status != 255 and msg.find('root') != -1:
            return True

        return False


    @classmethod
    def copy_logs(cls, cpfunc, src, dest):
        if not os.path.exists(dest):
            os.makedirs(dest)

        print "copy file %s -> %s" % (src, dest)
        return cpfunc(src, dest)


    @classmethod
    def org_peer_logs(cls, path, base):
        peer_path = path
        log_base = os.path.dirname(path)
        local_path = "%s%s%s" % (base, cls.pc.get_peer_hostname(), log_base) 

        try:
            ret = cls.copy_logs(cls.pc.copy_from_peer, peer_path, local_path)
            if ret != 0: 
                cls.logger.error('copy peer file: %s -> %s occured error. return code=[%d]' % (peer_path, local_path, ret))
            else:
                cls.logger.info('copy peer file: %s -> %s' % (peer_path, local_path))
        except (Exception, IOError) as e:
            cls.logger.error('copy peer file: %s -> %s occured error. %s' % (peer_path, local_path, str(e))) 


    @classmethod
    def org_local_logs(cls, path, base):
        src = path
        log_base = os.path.dirname(path)
        dest = "%s%s%s" % (base, cls.pc.get_hostname(), log_base) 
        try:
            # the return value is None if shutil.copy success
            cls.copy_logs(shutil.copy, src, dest)        
            cls.logger.info('copy local file: %s -> %s' % (src, dest))
        except (Exception, IOError) as e:
            cls.logger.error('copy local file: %s -> %s occured error. %s' % (src, dest, str(e))) 



    @classmethod
    def remove(cls, path):
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)


    @classmethod
    def mkdir_p(cls, path):
        if not os.path.exists(path):
            os.makedirs(path)


    @classmethod
    def fetch_log(cls, host, company_name, request_path):
        uri = "https://%s%s" % (host, request_path)
        conn, enc_fd = None, None 
        try:
	    conn = httplib.HTTPSConnection(host, timeout = 30)
    	    conn.request("GET", request_path)
    	    res = conn.getresponse()
            print uri, res.status, res.reason
    	    if res.status == 200:
    	        enc_fd = io.BytesIO()
    	        buf_w = io.BufferedWriter(enc_fd)

    	        while True:
                    # buffer size: 8192 bytes
    	    	    chunk = res.read(io.DEFAULT_BUFFER_SIZE)
                    if not chunk: break
                    buf_w.write(chunk)
    
                # write the rest of buffer data to memory
                buf_w.flush()
                # to prevent enc_fd be closed
                buf_w.detach()

                cls.logger.info("uri:[%s], size:[%d]" % (uri, enc_fd.tell()))
    	        enc_fd.seek(0)
    	    else:
    	        cls.logger.error("company:[%s], request:[%s%s], response:[%d][%s]" % (company_name, host, request_path, res.status, res.reason))
        except (ssl.SSLError, httplib.HTTPException) as e:
    	    cls.logger.error("uri:[%s] occurred problem. %s" % (uri, e))

        finally:
            if conn: conn.close()
            return enc_fd

        
    @classmethod
    def decrypt_in_mm(cls, enc_fd, cipher):
        zip_fd = io.BytesIO()
        buf_w = io.BufferedWriter(zip_fd)
        buf_r = io.BufferedReader(enc_fd)
        cipher.decrypt_fileobj(buf_r, buf_w)
        buf_w.flush()
        buf_w.detach()
        zip_fd.seek(0)
        return zip_fd

