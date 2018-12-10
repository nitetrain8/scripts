#include <Windows.h>
#include <Wlanapi.h>
#include <stdio.h>
#include <stdlib.h>
#include <atlbase.h>
#include <atlconv.h>

#define _CRT_SECURE_NO_WARNINGS


void _fail(int val, int line) {
	printf("Uh oh: %d at line %d\n", val, line);
}

#define fail(v) _fail(v, __LINE__);

HANDLE get_client(void) {
	DWORD res;
	DWORD negvers;
	HANDLE client;
	res = WlanOpenHandle(2, NULL, &negvers, &client);
	if (res != 0) {
		fail(res);
		return NULL;
	}
	return client;
}


LPOLESTR guid_str(GUID guid) {
	int sz = 256;
	LPOLESTR mem = (LPOLESTR)malloc(sz*sizeof(OLECHAR));
	if (!mem) {
		fail(-1);
		return NULL;
	}
	REFGUID g = guid; //cast
	int rv = StringFromGUID2(guid, mem, sz);
	if (rv == 0) {
		free(mem);
		fail(rv);
		return NULL;
	}
	return mem;
}

void guid_free(LPOLESTR s) {
	free(s);
}

void _scan(HANDLE client, GUID g) {
	DWORD res = WlanScan(client, &g, NULL, NULL, NULL);
	if (res) {
		fail(res);
	}
}

void _scan_client(HANDLE client, int v) {
	PWLAN_INTERFACE_INFO_LIST pii;
	DWORD res = WlanEnumInterfaces(client, NULL, &pii);
	if (res != 0) {
		fail(res);
	}
	WLAN_INTERFACE_INFO wii;
	GUID guid = { 0, 0, 0, 0 };
	for (int i = 0; i < (int)pii->dwNumberOfItems; i++) {
		wii = pii->InterfaceInfo[i];
		guid = wii.InterfaceGuid;
		if (v) {
			LPOLESTR s = guid_str(guid);
			char mem[256];
			wcstombs(mem, OLE2W(s), 255);
			printf("Scanning GUID %s\n", mem);
			guid_free(s);
		}
		_scan(client, guid);
	}
	WlanFreeMemory(pii);
}
#ifdef __cplusplus
extern "C"
{
	__declspec(dllexport) void scan(int verbose) {
		HANDLE client = get_client();
		_scan_client(client, verbose);
		if (verbose) {
			printf("Scan finished\n");
		}
		CloseHandle(client);
	}
}
#endif