/* teste-d3d11: cria o dispositivo Direct3D 11 em cada nível e grava o resultado num arquivo.
   Uso: teste-d3d11.exe [arquivo_de_saida] — sai normalmente para o DXVK gravar o log. */
#define COBJMACROS
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <stdio.h>

static const GUID IID_F1 = {0x770aae78, 0xf26f, 0x4dba, {0xa8, 0x29, 0x25, 0x3c, 0x83, 0xd1, 0xb3, 0x87}};

static const char *nome(D3D_FEATURE_LEVEL n) {
    switch (n) {
    case D3D_FEATURE_LEVEL_11_1: return "11_1";
    case D3D_FEATURE_LEVEL_11_0: return "11_0";
    case D3D_FEATURE_LEVEL_10_1: return "10_1";
    case D3D_FEATURE_LEVEL_10_0: return "10_0";
    case D3D_FEATURE_LEVEL_9_3: return "9_3";
    case D3D_FEATURE_LEVEL_9_1: return "9_1";
    default: return "?";
    }
}

static int teste(void) {
    const char *arq = "D:\\diag\\teste-d3d11.txt";
    FILE *f = fopen(arq, "w");
    if (!f) f = stdout;
    IDXGIFactory1 *fab = NULL;
    HRESULT hr = CreateDXGIFactory1(&IID_F1, (void **)&fab);
    fprintf(f, "CreateDXGIFactory1: 0x%08lx\n", (unsigned long)hr);
    if (SUCCEEDED(hr)) {
        IDXGIAdapter1 *ad = NULL;
        for (UINT i = 0; IDXGIFactory1_EnumAdapters1(fab, i, &ad) != DXGI_ERROR_NOT_FOUND; i++) {
            DXGI_ADAPTER_DESC1 d;
            IDXGIAdapter1_GetDesc1(ad, &d);
            fprintf(f, "adaptador %u: %ls vendor=%04x device=%04x vram=%llu MB\n", i, d.Description,
                    d.VendorId, d.DeviceId, (unsigned long long)(d.DedicatedVideoMemory >> 20));
            IDXGIAdapter1_Release(ad);
        }
        IDXGIFactory1_Release(fab);
    }
    D3D_FEATURE_LEVEL niveis[] = {D3D_FEATURE_LEVEL_11_1, D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_1,
                                  D3D_FEATURE_LEVEL_10_0, D3D_FEATURE_LEVEL_9_3, D3D_FEATURE_LEVEL_9_1};
    for (int i = 0; i < 6; i++) {
        ID3D11Device *dev = NULL;
        ID3D11DeviceContext *ctx = NULL;
        D3D_FEATURE_LEVEL obtido = 0;
        hr = D3D11CreateDevice(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, 0, &niveis[i], 1, D3D11_SDK_VERSION,
                               &dev, &obtido, &ctx);
        fprintf(f, "D3D11CreateDevice nivel %s: 0x%08lx%s\n", nome(niveis[i]), (unsigned long)hr,
                SUCCEEDED(hr) ? " OK" : "");
        fflush(f);
        if (ctx) ID3D11DeviceContext_Release(ctx);
        if (dev) ID3D11Device_Release(dev);
    }
    {
        ID3D11Device *dev = NULL;
        D3D_FEATURE_LEVEL obtido = 0;
        hr = D3D11CreateDevice(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, D3D11_CREATE_DEVICE_BGRA_SUPPORT, niveis + 1, 3,
                               D3D11_SDK_VERSION, &dev, &obtido, NULL);
        fprintf(f, "D3D11CreateDevice BGRA [11_0..10_0]: 0x%08lx nivel=%s\n", (unsigned long)hr,
                SUCCEEDED(hr) ? nome(obtido) : "-");
        if (dev) ID3D11Device_Release(dev);
    }
    fprintf(f, "fim\n");
    if (f != stdout) fclose(f);
    return 0;
}

void __stdcall entrada(void) { ExitProcess((UINT)teste()); }
