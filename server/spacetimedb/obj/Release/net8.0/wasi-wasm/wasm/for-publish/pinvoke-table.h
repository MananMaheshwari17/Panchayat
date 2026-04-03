// GENERATED FILE, DO NOT MODIFY

int bytes_sink_write (int,int,int);
int bytes_source_read (int,int,int);
int bytes_source_remaining_length (int,int);
void console_log (int,int,int,int,int,int,int,int);
int datastore_delete_all_by_eq_bsatn (int,int,int,int);
int datastore_insert_bsatn (int,int,int);
int datastore_table_scan_bsatn (int,int);
int get_jwt (int,int);
void identity (int);
int row_iter_bsatn_advance (int,int,int);
int row_iter_bsatn_close (int);
int SystemNative_Close (int);
int SystemNative_CloseDir (int);
int SystemNative_ConvertErrorPalToPlatform (int);
int SystemNative_ConvertErrorPlatformToPal (int);
int SystemNative_FAllocate (int,int64_t,int64_t);
int SystemNative_FLock (int,int);
void SystemNative_Free (int);
int SystemNative_FStat (int,int);
int SystemNative_FTruncate (int,int64_t);
int SystemNative_GetCwd (int,int);
int SystemNative_GetEnv (int);
int SystemNative_GetErrNo ();
int SystemNative_GetFileSystemType (int);
void SystemNative_GetNonCryptographicallySecureRandomBytes (int,int);
int SystemNative_GetReadDirRBufferSize ();
int64_t SystemNative_GetSystemTimeAsTicks ();
uint64_t SystemNative_GetTimestamp ();
int SystemNative_GetTimeZoneData (int,int);
void SystemNative_LowLevelMonitor_Acquire (int);
int SystemNative_LowLevelMonitor_Create ();
void SystemNative_LowLevelMonitor_Destroy (int);
void SystemNative_LowLevelMonitor_Release (int);
void SystemNative_LowLevelMonitor_Signal_Release (int);
int SystemNative_LowLevelMonitor_TimedWait (int,int);
void SystemNative_LowLevelMonitor_Wait (int);
int64_t SystemNative_LSeek (int,int64_t,int);
int SystemNative_LStat (int,int);
int SystemNative_Malloc (int);
int SystemNative_Open (int,int,int);
int SystemNative_OpenDir (int);
int SystemNative_PosixFAdvise (int,int64_t,int64_t,int);
int SystemNative_PRead (int,int,int,int64_t);
int SystemNative_Read (int,int,int);
int SystemNative_ReadDirR (int,int,int,int);
int SystemNative_ReadLink (int,int,int);
int SystemNative_SchedGetCpu ();
void SystemNative_SetErrNo (int);
int SystemNative_Stat (int,int);
int SystemNative_StrErrorR (int,int,int);
int SystemNative_Unlink (int);
int table_id_from_name (int,int,int);
static PinvokeImport bindings_imports [] = {
{"bytes_sink_write", bytes_sink_write}, // SpacetimeDB.Runtime
{"bytes_source_read", bytes_source_read}, // SpacetimeDB.Runtime
{"bytes_source_remaining_length", bytes_source_remaining_length}, // SpacetimeDB.Runtime
{"console_log", console_log}, // SpacetimeDB.Runtime
{"datastore_delete_all_by_eq_bsatn", datastore_delete_all_by_eq_bsatn}, // SpacetimeDB.Runtime
{"datastore_insert_bsatn", datastore_insert_bsatn}, // SpacetimeDB.Runtime
{"datastore_table_scan_bsatn", datastore_table_scan_bsatn}, // SpacetimeDB.Runtime
{"get_jwt", get_jwt}, // SpacetimeDB.Runtime
{"identity", identity}, // SpacetimeDB.Runtime
{"row_iter_bsatn_advance", row_iter_bsatn_advance}, // SpacetimeDB.Runtime
{"row_iter_bsatn_close", row_iter_bsatn_close}, // SpacetimeDB.Runtime
{"table_id_from_name", table_id_from_name}, // SpacetimeDB.Runtime
{NULL, NULL}
};
static PinvokeImport libicudata_imports [] = {
{NULL, NULL}
};
static PinvokeImport libicui18n_imports [] = {
{NULL, NULL}
};
static PinvokeImport libicuuc_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_debugger_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_debugger_stub_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_diagnostics_tracing_stub_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_hot_reload_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_hot_reload_stub_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_marshal_ilgen_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_component_marshal_ilgen_stub_static_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_ee_interp_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_icall_table_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmono_wasm_nosimd_imports [] = {
{NULL, NULL}
};
static PinvokeImport libmonosgen_2_0_imports [] = {
{NULL, NULL}
};
static PinvokeImport libSystem_Globalization_Native_imports [] = {
{NULL, NULL}
};
static PinvokeImport libSystem_IO_Compression_Native_imports [] = {
{NULL, NULL}
};
static PinvokeImport libSystem_Native_imports [] = {
{"SystemNative_Close", SystemNative_Close}, // System.Private.CoreLib
{"SystemNative_CloseDir", SystemNative_CloseDir}, // System.Private.CoreLib
{"SystemNative_ConvertErrorPalToPlatform", SystemNative_ConvertErrorPalToPlatform}, // System.Private.CoreLib
{"SystemNative_ConvertErrorPlatformToPal", SystemNative_ConvertErrorPlatformToPal}, // System.Private.CoreLib
{"SystemNative_FAllocate", SystemNative_FAllocate}, // System.Private.CoreLib
{"SystemNative_FLock", SystemNative_FLock}, // System.Private.CoreLib
{"SystemNative_Free", SystemNative_Free}, // System.Private.CoreLib
{"SystemNative_FStat", SystemNative_FStat}, // System.Private.CoreLib
{"SystemNative_FTruncate", SystemNative_FTruncate}, // System.Private.CoreLib
{"SystemNative_GetCwd", SystemNative_GetCwd}, // System.Private.CoreLib
{"SystemNative_GetEnv", SystemNative_GetEnv}, // System.Private.CoreLib
{"SystemNative_GetErrNo", SystemNative_GetErrNo}, // System.Private.CoreLib
{"SystemNative_GetFileSystemType", SystemNative_GetFileSystemType}, // System.Private.CoreLib
{"SystemNative_GetNonCryptographicallySecureRandomBytes", SystemNative_GetNonCryptographicallySecureRandomBytes}, // System.Private.CoreLib
{"SystemNative_GetReadDirRBufferSize", SystemNative_GetReadDirRBufferSize}, // System.Private.CoreLib
{"SystemNative_GetSystemTimeAsTicks", SystemNative_GetSystemTimeAsTicks}, // System.Private.CoreLib
{"SystemNative_GetTimestamp", SystemNative_GetTimestamp}, // System.Private.CoreLib
{"SystemNative_GetTimeZoneData", SystemNative_GetTimeZoneData}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Acquire", SystemNative_LowLevelMonitor_Acquire}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Create", SystemNative_LowLevelMonitor_Create}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Destroy", SystemNative_LowLevelMonitor_Destroy}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Release", SystemNative_LowLevelMonitor_Release}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Signal_Release", SystemNative_LowLevelMonitor_Signal_Release}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_TimedWait", SystemNative_LowLevelMonitor_TimedWait}, // System.Private.CoreLib
{"SystemNative_LowLevelMonitor_Wait", SystemNative_LowLevelMonitor_Wait}, // System.Private.CoreLib
{"SystemNative_LSeek", SystemNative_LSeek}, // System.Private.CoreLib
{"SystemNative_LStat", SystemNative_LStat}, // System.Private.CoreLib
{"SystemNative_Malloc", SystemNative_Malloc}, // System.Private.CoreLib
{"SystemNative_Open", SystemNative_Open}, // System.Private.CoreLib
{"SystemNative_OpenDir", SystemNative_OpenDir}, // System.Private.CoreLib
{"SystemNative_PosixFAdvise", SystemNative_PosixFAdvise}, // System.Private.CoreLib
{"SystemNative_PRead", SystemNative_PRead}, // System.Private.CoreLib
{"SystemNative_Read", SystemNative_Read}, // System.Private.CoreLib
{"SystemNative_ReadDirR", SystemNative_ReadDirR}, // System.Private.CoreLib
{"SystemNative_ReadLink", SystemNative_ReadLink}, // System.Private.CoreLib
{"SystemNative_SchedGetCpu", SystemNative_SchedGetCpu}, // System.Private.CoreLib
{"SystemNative_SetErrNo", SystemNative_SetErrNo}, // System.Private.CoreLib
{"SystemNative_Stat", SystemNative_Stat}, // System.Private.CoreLib
{"SystemNative_StrErrorR", SystemNative_StrErrorR}, // System.Private.CoreLib
{"SystemNative_Unlink", SystemNative_Unlink}, // System.Private.CoreLib
{NULL, NULL}
};
static PinvokeImport wasm_bundled_timezones_imports [] = {
{NULL, NULL}
};
static PinvokeImport libc___imports [] = {
{NULL, NULL}
};
static PinvokeImport libc__abi_imports [] = {
{NULL, NULL}
};
static void *pinvoke_tables[] = { bindings_imports,libicudata_imports,libicui18n_imports,libicuuc_imports,libmono_component_debugger_static_imports,libmono_component_debugger_stub_static_imports,libmono_component_diagnostics_tracing_stub_static_imports,libmono_component_hot_reload_static_imports,libmono_component_hot_reload_stub_static_imports,libmono_component_marshal_ilgen_static_imports,libmono_component_marshal_ilgen_stub_static_imports,libmono_ee_interp_imports,libmono_icall_table_imports,libmono_wasm_nosimd_imports,libmonosgen_2_0_imports,libSystem_Globalization_Native_imports,libSystem_IO_Compression_Native_imports,libSystem_Native_imports,wasm_bundled_timezones_imports,libc___imports,libc__abi_imports,};
static char *pinvoke_names[] = { "bindings","libicudata","libicui18n","libicuuc","libmono-component-debugger-static","libmono-component-debugger-stub-static","libmono-component-diagnostics_tracing-stub-static","libmono-component-hot_reload-static","libmono-component-hot_reload-stub-static","libmono-component-marshal-ilgen-static","libmono-component-marshal-ilgen-stub-static","libmono-ee-interp","libmono-icall-table","libmono-wasm-nosimd","libmonosgen-2.0","libSystem.Globalization.Native","libSystem.IO.Compression.Native","libSystem.Native","wasm-bundled-timezones","libc++","libc++abi",};
InterpFtnDesc wasm_native_to_interp_ftndescs[1];
typedef void  (*WasmInterpEntrySig_0) (int*,int*,int*,int*,int*,int*,int*,int*);
int wasm_native_to_interp_System_Private_CoreLib_ComponentActivator_GetFunctionPointer (int arg0,int arg1,int arg2,int arg3,int arg4,int arg5) { 
int res;
((WasmInterpEntrySig_0)wasm_native_to_interp_ftndescs [0].func) ((int*)&res, (int*)&arg0, (int*)&arg1, (int*)&arg2, (int*)&arg3, (int*)&arg4, (int*)&arg5, wasm_native_to_interp_ftndescs [0].arg);
return res;
}
static void *wasm_native_to_interp_funcs[] = { wasm_native_to_interp_System_Private_CoreLib_ComponentActivator_GetFunctionPointer,};
static const char *wasm_native_to_interp_map[] = { "System_Private_CoreLib_ComponentActivator_GetFunctionPointer",
};
