"""Manual SDK installation helper; no download on import or by default."""
import argparse
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--metadata',type=__import__('pathlib').Path);p.add_argument('--output-dir',type=__import__('pathlib').Path,default=__import__('pathlib').Path('.local/sdk-cache'));args=p.parse_args()
 if not args.execute:print('Manual installation helper only. No SDK download without --execute and official metadata.');return
 if not args.metadata or not args.metadata.is_file():p.error('official sdk-releases metadata file required')
 import concurrent.futures, subprocess, pathlib, hashlib, json
 root=args.output_dir.resolve(); root.mkdir(parents=True,exist_ok=True)
 url='https://builds.dotnet.microsoft.com/dotnet/Sdk/8.0.425/dotnet-sdk-8.0.425-win-x64.zip'
 size=285157731
 def fetch(i):
     a=size*i//16; b=size*(i+1)//16-1
     p=root/f'sdk.part{i}'
     subprocess.run(['curl.exe','-L','--fail','--retry','2','--max-time','600','-sS','-r',f'{a}-{b}',url,'-o',str(p)],check=True)
     if p.stat().st_size!=b-a+1: raise RuntimeError('Wrong range length')
     print(f'part {i+1}/16 ready',flush=True)
     return p
 with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
     parts=list(pool.map(fetch,range(16)))
 out=root/'sdk-verified.zip'
 h=hashlib.sha512()
 with out.open('wb') as w:
     for p in parts:
         with p.open('rb') as r:
             while data:=r.read(1024*1024): w.write(data); h.update(data)
 meta=json.loads((args.metadata).read_text(encoding='utf-8-sig'))
 expected=next(f['hash'] for f in meta['releases'][0]['sdk']['files'] if f['rid']=='win-x64' and f['name'].endswith('.zip'))
 assert h.hexdigest().lower()==expected.lower(), 'SDK SHA512 mismatch'
 print('SDK SHA512 verified',flush=True)

if __name__=='__main__':main()
