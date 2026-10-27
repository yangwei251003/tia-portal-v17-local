"""Source-archive checks only: no TIA launch, PLC connection or SDK binary."""
import ast,json,xml.etree.ElementTree as ET
from pathlib import Path

def main():
 root=Path(__file__).resolve().parents[1]
 for rel in ['LICENSE','tools/tiaportal-mcp/src/TiaMcpServer/TiaMcpServer.V17.csproj','tools/tiaportal-mcp/src/TiaMcpServer/ModelContextProtocol/PlcSoftwareV17LocalTools.cs','templates/project-blueprints/full_plc_hmi_project.json']:
  assert (root/rel).is_file(),rel
 counts={'json':0,'xml':0,'python':0}
 for p in root.rglob('*'):
  if not p.is_file() or any(v in p.relative_to(root).parts for v in ['.git','.local','__pycache__','bin','obj','bin-v17','obj-v17']):continue
  assert p.suffix.lower() not in ['.dll','.exe','.pdb','.pfx','.p12','.zip'],p.name
  if p.suffix=='.json':json.loads(p.read_text('utf-8-sig'));counts['json']+=1
  if p.suffix.lower() in ['.xml','.csproj']:
   s=p.read_text('utf-8-sig');assert '<!DOCTYPE' not in s.upper();ET.fromstring(s);counts['xml']+=1
  if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'));counts['python']+=1
 print(json.dumps({'source_checks':counts,'binary_or_private_config_required':False,'TIA_started':False,'PLC_operation':False},indent=2))

if __name__=='__main__':main()
