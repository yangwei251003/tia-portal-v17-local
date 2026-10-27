# 来源、增量与实际验证

上游bulaofen0036-coder/TIA_Portal_Openness_MCP，原HEAD70758f2b7359021fefb674c099c1c8eddbba44e1，MIT。原本机162跟踪/95未跟踪路径，实际257文件；SDK分片/归档/本地DLL等安装缓存占绝大部分，不作为源码上传。

主体增量是V17工具类partial与LocalTools三个方法。原手动probe/configure/test代码属于本地集成、安装和验收辅助，不冒称新的PLC内核。保留等价的配置输出/手动集成/分段下载代码，改为显式执行，不保存个人config或固定个人路径；原私有验证JSON、SDK元数据/日志、下载归档和DLL不分发。

V17用已有.NET8.0.425、.NETFramework4.8及官方NuGet引用成功构建，0错误3nullable警告。编译缓存/输出均留私有工作区。真实离线HMI六项均通过；真实stdio initialize/tools-list发现65工具含3新增，未发工程tools/call。没有启动/附着TIA工程、连接PLC或做下载/RUN。

上游PLC Builder依赖5份原导出金样本，源码包不含这些文件。首跑因UDT_Fault.xml缺失而崩溃；最小修补是在readiness失败时生成blocked报告并返回退出2，不执行Builder。真实编译CLI的空目录回归验证了这一行为。未从生成器反向制造“金样本”来凑通过。

V20/V21未构建；在线读写、硬件、WinCC、模拟/真实下载等没有验收。原厂手册/商业组件应由使用者按官方许可自行获取；本仓库的源代码可阅读/编译条件说明不等于产品授权或生产安全认证。
