using ModelContextProtocol.Server;
using System;
using System.ComponentModel;
using System.Collections.Generic;
using Siemens.Engineering;
using Siemens.Engineering.Download;
using Siemens.Engineering.Download.Configurations;
using Siemens.Engineering.Connection;

namespace TiaMcpServer.ModelContextProtocol
{
    public static partial class PlcSoftwareV17McpTools
    {
        [McpServerTool(Name = "OpenLadderEditor"), Description("Open an existing root PLC block in the TIA editor; no PLC download.")]
        public static object OpenLadderEditor(string softwarePath, string blockName = "Main")
        {
            var sw = McpServer.Portal.GetPlcSoftware(softwarePath) ?? throw new InvalidOperationException("PLC software not found");
            var block = sw.BlockGroup.Blocks.Find(blockName) ?? throw new InvalidOperationException("Block not found");
            block.ShowInEditor();
            return new { success = true, blockName, language = block.ProgrammingLanguage.ToString(), action = "ShowInEditor completed" };
        }

        [McpServerTool(Name = "InspectSimulationDownloadInterfaces"), Description("Read-only enumerate configured download interfaces, without connecting or downloading to any PLC.")]
        public static object InspectSimulationDownloadInterfaces(string softwarePath)
        {
            var sw = McpServer.Portal.GetPlcSoftware(softwarePath) ?? throw new InvalidOperationException("PLC software not found");
            DownloadProvider? provider = null;
            IEngineeringObject obj = sw;
            while (obj != null && provider == null)
            {
                if (obj is IEngineeringServiceProvider sp) provider = sp.GetService<DownloadProvider>();
                obj = obj.Parent;
            }
            if (provider == null) return new { success = false, message = "DownloadProvider unavailable" };
            var rows = new List<object>();
            foreach (var mode in provider.Configuration.Modes)
                foreach (var pc in mode.PcInterfaces)
                {
                    var targets = new List<object>();
                    foreach (var target in pc.TargetInterfaces)
                    {
                        var addresses = new List<object>();
                        foreach (var address in target.Addresses) addresses.Add(new { address.Name, address.Address });
                        targets.Add(new { target.Name, addresses });
                    }
                    rows.Add(new { mode = mode.Name, name = pc.Name, number = pc.Number, targets });
                }
            return new { success = true, interfaces = rows, readOnly = true };
        }

        [McpServerTool(Name = "DownloadTestProjectToPlcsimAndRun"), Description("Download only the LAD_Simulation_20260909 test PLC using exact PLCSIM virtual interface and request RUN after download. Requires previously inspected target interface and address; never falls back to physical adapters.")]
        public static object DownloadTestProjectToPlcsimAndRun(string targetInterfaceName, string targetAddress, int pcInterfaceNumber)
        {
            const string path = "PLC_Simulation/PLC_Simulation";
            var sw = McpServer.Portal.GetPlcSoftware(path) ?? throw new InvalidOperationException("Test PLC missing");
            IEngineeringObject obj = sw;
            DownloadProvider? provider = null;
            Project? project = null;
            while (obj != null)
            {
                if (provider == null && obj is IEngineeringServiceProvider sp) provider = sp.GetService<DownloadProvider>();
                if (obj is Project p) project = p;
                obj = obj.Parent;
            }
            if (project == null || project.Name != "LAD_Simulation_20260909") throw new InvalidOperationException("Only isolated test project allowed");
            if (provider == null) throw new InvalidOperationException("Download provider unavailable");
            var mode = provider.Configuration.Modes.Find("PN/IE") ?? throw new InvalidOperationException("PN/IE missing");
            var pc = mode.PcInterfaces.Find("PLCSIM", pcInterfaceNumber) ?? throw new InvalidOperationException("Exact virtual PLCSIM interface missing");
            var target = pc.TargetInterfaces.Find(targetInterfaceName) ?? throw new InvalidOperationException("Inspected target interface missing");
            ConfigurationAddress? selected = null;
            foreach (var a in target.Addresses) if (a.Address == targetAddress) selected = a;
            if (selected == null) throw new InvalidOperationException("Inspected target address missing");
            var callbacks = new List<string>();
            bool startRequested = false;
            DownloadConfigurationDelegate pre = c => {
                callbacks.Add("pre:" + c.GetType().Name);
                if (c is StopModules stop) stop.CurrentSelection = StopModulesSelections.StopAll;
            };
            DownloadConfigurationDelegate post = c => {
                callbacks.Add("post:" + c.GetType().Name);
                if (c is StartModules start) { start.CurrentSelection = StartModulesSelections.StartModule; startRequested = true; }
            };
            var result = provider.Download(selected, pre, post, DownloadOptions.Hardware | DownloadOptions.Software);
            return new { state = result.State.ToString(), result.ErrorCount, result.WarningCount, startRequested, callbacks, adapter = "PLCSIM", targetAddress, runVerified = false };
        }
    }
}
