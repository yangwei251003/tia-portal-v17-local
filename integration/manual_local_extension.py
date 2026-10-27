"""Manual live TIA example retained from the local work tree. Not run by tests."""
import argparse
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--server-exe',type=__import__('pathlib').Path);parser.add_argument('--project-name');parser.add_argument('--software-path');parser.add_argument('--output-dir',type=__import__('pathlib').Path,default=__import__('pathlib').Path('.local/manual-live'))
 args=parser.parse_args()
 if not args.execute:
  print('Manual live example only. This may attach to a TIA project and open its editor; no action without --execute and explicit targets.');return
 if not all([args.server_exe,args.project_name,args.software_path]):parser.error('explicit server-exe, project-name and software-path required')
 import subprocess,json,threading,queue,pathlib,time
 root=args.output_dir.resolve(); root.mkdir(parents=True,exist_ok=True)
 p=subprocess.Popen([str(args.server_exe.resolve()),'--tool-profile','plc-software-v17-phase1','--tia-major-version','17','--tia-portal-location',r'C:\Program Files\Siemens\Automation\Portal V17','--with-ui'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(root/'local-extension-stderr.log').open('w'),text=True,encoding='utf-8')
 q=queue.Queue()
 def reader():
  for line in p.stdout:
   try:q.put(json.loads(line))
   except ValueError:pass
 threading.Thread(target=reader,daemon=True).start()
 def call(i,method,params):
  p.stdin.write(json.dumps(dict(jsonrpc='2.0',id=i,method=method,params=params))+'\n');p.stdin.flush()
  end=time.time()+180
  while time.time()<end:
   try:r=q.get(timeout=1)
   except queue.Empty:continue
   if r.get('id')==i:
    (root/f'extension-result-{i}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False),flush=True);return
  raise TimeoutError(method)
 try:
  call(1,'initialize',dict(protocolVersion='2024-11-05',capabilities={},clientInfo=dict(name='local-extension-test',version='1.0')))
  p.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n');p.stdin.flush()
  call(2,'tools/call',dict(name='AttachToOpenProject',arguments=dict(projectName=args.project_name)))
  call(3,'tools/call',dict(name='OpenLadderEditor',arguments=dict(softwarePath=args.software_path,blockName='Main')))
  call(4,'tools/call',dict(name='InspectSimulationDownloadInterfaces',arguments=dict(softwarePath=args.software_path)))
 finally:
  p.stdin.close()
  try:p.wait(timeout=5)
  except subprocess.TimeoutExpired:p.terminate()

if __name__=='__main__':main()
