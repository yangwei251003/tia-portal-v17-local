"""Metadata-only stdio probe; initialize/list tools, never call a TIA tool."""
import argparse,ctypes,json,os,queue,subprocess,threading,time
from pathlib import Path

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--server-exe',type=Path,required=True);parser.add_argument('--work-dir',type=Path,default=Path('.local/stdio-metadata'));a=parser.parse_args();work=a.work_dir.resolve();work.mkdir(parents=True,exist_ok=True);tmp=work/'tmp';tmp.mkdir(exist_ok=True)
 if os.name=='nt':ctypes.windll.kernel32.SetErrorMode(3)
 env={**os.environ,'TMP':str(tmp),'TEMP':str(tmp)}
 with (work/'server-stderr.log').open('w',encoding='utf8') as err:
  p=subprocess.Popen([str(a.server_exe.resolve()),'--tool-profile','plc-software-v17-phase1','--tia-major-version','17','--without-ui'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf8',env=env,creationflags=0x08000000 if os.name=='nt' else 0)
  responses=queue.Queue()
  def reader():
   for line in p.stdout:
    try:responses.put(json.loads(line))
    except ValueError:pass
  threading.Thread(target=reader,daemon=True).start()
  def call(number,method,params):
   p.stdin.write(json.dumps({'jsonrpc':'2.0','id':number,'method':method,'params':params})+'\n');p.stdin.flush();end=time.monotonic()+60
   while time.monotonic()<end:
    try:r=responses.get(timeout=1)
    except queue.Empty:
     if p.poll() is not None:raise RuntimeError('MCP process exited')
     continue
    if r.get('id')==number:
     assert 'error' not in r,r['error'];return r['result']
   raise TimeoutError(method)
  try:
   call(1,'initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'offline-metadata-only','version':'1'}})
   p.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n');p.stdin.flush()
   result=call(2,'tools/list',{});names=[v['name'] for v in result['tools']]
   expected={'OpenLadderEditor','InspectSimulationDownloadInterfaces','DownloadTestProjectToPlcsimAndRun'};assert expected<=set(names),expected-set(names)
   summary={'stdio_initialized':True,'tool_count':len(names),'local_tools_visible':sorted(expected),'tools_called':0,'TIA_connection_requested':False,'PLC_operation_requested':False};(work/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary,indent=2))
  finally:
   p.stdin.close()
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=10)

if __name__=='__main__':main()
