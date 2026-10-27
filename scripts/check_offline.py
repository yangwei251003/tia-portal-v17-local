"""Run real compiled CLI offline checks; never invoke a PLC/TIA tool."""
import argparse,ctypes,json,os,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--server-exe',type=Path,required=True);p.add_argument('--work-dir',type=Path,default=Path('.local/offline-check'));p.add_argument('--tia-path',default='C:/Program Files/Siemens/Automation/Portal V17');a=p.parse_args()
 root=Path(__file__).resolve().parents[1];work=a.work_dir.resolve();work.mkdir(parents=True,exist_ok=True);tmp=work/'tmp';tmp.mkdir(exist_ok=True)
 if os.name=='nt':ctypes.windll.kernel32.SetErrorMode(3)
 env={**os.environ,'TEMP':str(tmp),'TMP':str(tmp)};exe=a.server_exe.resolve();assert exe.is_file()
 base=[str(exe),'--tia-major-version','17','--tia-portal-location',a.tia_path,'--without-ui']
 hmi=work/'hmi';r=subprocess.run(base+['--run-classic-hmi-offline-suite','--classic-hmi-offline-suite-report-directory',str(hmi)],cwd=root,env=env,capture_output=True,encoding='utf8',errors='replace',timeout=90)
 (work/'hmi.log').write_text(r.stdout+r.stderr,encoding='utf8');assert r.returncode==0,r.returncode
 h=json.loads(next(hmi.glob('classic_hmi_offline_validation_suite_*.json')).read_text('utf-8-sig'));assert h['ok'] and h['offlineOnly'] and all(v['ok'] for v in h['items'])
 empty=work/'empty-fixture';empty.mkdir(exist_ok=True);assert not any(empty.iterdir())
 plc=work/'plc';r=subprocess.run(base+['--run-plc-builder-offline-suite','--plc-export-directory',str(empty),'--plc-builder-suite-report-directory',str(plc)],cwd=root,env=env,capture_output=True,encoding='utf8',errors='replace',timeout=90)
 (work/'plc.log').write_text(r.stdout+r.stderr,encoding='utf8');assert r.returncode==2,r.returncode
 d=json.loads(next(plc.glob('plc_builder_offline_suite_blocked_*.json')).read_text('utf-8-sig'));assert d['blocked'] and not d['ok'];assert d['fixtureReadiness']['summary']['fail']==5
 result={'hmi_offline_cases':len(h['items']),'hmi_all_pass':True,'missing_plc_fixture_reports_blocked':True,'missing_fixture_exit_code':2,'missing_golden_fixtures':5,'real_TIA_connection':False,'PLC_operation':False,'scope':'Real compiled CLI. Positive self-contained HMI fixture suite and negative missing-PLC-golden precondition only; no online/TIA-import/physical verification.'}
 (work/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
