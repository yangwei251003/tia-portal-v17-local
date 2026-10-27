"""Render an explicit configuration snippet only; never edit a user's config."""
import argparse,json
def main():
 p=argparse.ArgumentParser();p.add_argument('--server-exe',required=True);p.add_argument('--tia-path',default='C:/Program Files/Siemens/Automation/Portal V17');a=p.parse_args()
 args=['--tool-profile','plc-software-v17-phase1','--tia-major-version','17','--tia-portal-location',a.tia_path,'--with-ui']
 print('[mcp_servers.tia_portal_v17]\ncommand = '+json.dumps(a.server_exe)+'\nargs = '+json.dumps(args)+'\nstartup_timeout_sec = 120\ntool_timeout_sec = 180')
if __name__=='__main__':main()
