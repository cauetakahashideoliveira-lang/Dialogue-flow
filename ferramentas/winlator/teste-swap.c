/* teste-swap: cria um dispositivo D3D11 e tenta swapchains DXGI numa janela normal e numa janela-filha
   (as janelas de plugin do Studio são filhas). Grava tudo em D:\diag\teste-swap.txt e sai normalmente. */
#define COBJMACROS
#include <windows.h>
#include <d3d11.h>
#include <dxgi1_2.h>
#include <stdio.h>

static const GUID IID_Dev = {0x54ec77fa, 0x1377, 0x44e6, {0x8c, 0x32, 0x88, 0xfd, 0x5f, 0x44, 0xc8, 0x4c}};  /* IDXGIDevice */
static const GUID IID_F2 = {0x50c83a1c, 0xe072, 0x4c48, {0x87, 0xb0, 0x36, 0x30, 0xfa, 0x36, 0xa6, 0xd0}};   /* IDXGIFactory2 */

static LRESULT CALLBACK proc(HWND h, UINT m, WPARAM w, LPARAM l) { return DefWindowProcA(h, m, w, l); }

static void tenta(FILE *f, IDXGIFactory2 *fab, IUnknown *dev, HWND w, const char *janela, HWND pai) {
    struct { const char *nome; DXGI_SWAP_EFFECT ef; UINT n; DXGI_SCALING esc; DXGI_ALPHA_MODE alfa; } c[] = {
        {"flip_premult", DXGI_SWAP_EFFECT_FLIP_DISCARD, 2, DXGI_SCALING_STRETCH, DXGI_ALPHA_MODE_PREMULTIPLIED},
        {"flip_discard", DXGI_SWAP_EFFECT_FLIP_DISCARD, 2, DXGI_SCALING_STRETCH, DXGI_ALPHA_MODE_UNSPECIFIED},
        {"flip_premult_de_novo", DXGI_SWAP_EFFECT_FLIP_DISCARD, 2, DXGI_SCALING_STRETCH, DXGI_ALPHA_MODE_PREMULTIPLIED},
        {"flip_ignore", DXGI_SWAP_EFFECT_FLIP_DISCARD, 2, DXGI_SCALING_STRETCH, DXGI_ALPHA_MODE_IGNORE},
    };
    for (int i = 0; i < 4; i++) {
        DXGI_SWAP_CHAIN_DESC1 d = {0};
        d.Format = DXGI_FORMAT_B8G8R8A8_UNORM;
        d.SampleDesc.Count = 1;
        d.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
        d.BufferCount = c[i].n;
        d.SwapEffect = c[i].ef;
        d.Scaling = c[i].esc;
        d.AlphaMode = c[i].alfa;
        IDXGISwapChain1 *sc = NULL;
        HWND alvo = w;
        if (pai) alvo = CreateWindowExA(0, "testeSwap", "filha", WS_CHILD | WS_VISIBLE, 10 + 20 * i, 10, 320, 240, pai,
                                        NULL, GetModuleHandleA(NULL), NULL);
        HRESULT hr = IDXGIFactory2_CreateSwapChainForHwnd(fab, dev, alvo, &d, NULL, NULL, &sc);
        fprintf(f, "%s %s: 0x%08lx%s\n", janela, c[i].nome, (unsigned long)hr, SUCCEEDED(hr) ? " OK" : "");
        fflush(f);
        if (sc) IDXGISwapChain1_Release(sc);
        Sleep(300);
    }
}

static int teste(void) {
    FILE *f = fopen("D:\\diag\\teste-swap.txt", "w");
    if (!f) return 1;
    WNDCLASSA wc = {0};
    wc.lpfnWndProc = proc;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "testeSwap";
    RegisterClassA(&wc);
    HWND topo = CreateWindowExA(0, "testeSwap", "teste-swap", WS_OVERLAPPEDWINDOW | WS_VISIBLE, 50, 50, 640, 480,
                                NULL, NULL, wc.hInstance, NULL);
    HWND filha = CreateWindowExA(0, "testeSwap", "filha", WS_CHILD | WS_VISIBLE, 10, 10, 320, 240, topo, NULL,
                                 wc.hInstance, NULL);
    fprintf(f, "janelas: topo=%p filha=%p\n", (void *)topo, (void *)filha);
    D3D_FEATURE_LEVEL niveis[] = {D3D_FEATURE_LEVEL_11_0, D3D_FEATURE_LEVEL_10_1, D3D_FEATURE_LEVEL_10_0};
    ID3D11Device *dev = NULL;
    D3D_FEATURE_LEVEL obtido = 0;
    HRESULT hr = D3D11CreateDevice(NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, D3D11_CREATE_DEVICE_BGRA_SUPPORT, niveis, 3,
                                   D3D11_SDK_VERSION, &dev, &obtido, NULL);
    fprintf(f, "D3D11CreateDevice: 0x%08lx nivel=0x%x\n", (unsigned long)hr, (unsigned)obtido);
    if (FAILED(hr)) { fclose(f); return 2; }
    IDXGIDevice *dd = NULL;
    IDXGIAdapter *ad = NULL;
    IDXGIFactory2 *fab = NULL;
    ID3D11Device_QueryInterface(dev, &IID_Dev, (void **)&dd);
    IDXGIDevice_GetAdapter(dd, &ad);
    DXGI_ADAPTER_DESC desc;
    IDXGIAdapter_GetDesc(ad, &desc);
    fprintf(f, "adaptador: %ls\n", desc.Description);
    hr = IDXGIAdapter_GetParent(ad, &IID_F2, (void **)&fab);
    fprintf(f, "IDXGIFactory2: 0x%08lx\n", (unsigned long)hr);
    if (SUCCEEDED(hr)) {
        tenta(f, fab, (IUnknown *)dev, topo, "topo", NULL);
        tenta(f, fab, (IUnknown *)dev, filha, "filha_nova", topo);
        IDXGIFactory2_Release(fab);
    }
    IDXGIAdapter_Release(ad);
    IDXGIDevice_Release(dd);
    ID3D11Device_Release(dev);
    DestroyWindow(topo);
    fprintf(f, "fim\n");
    fclose(f);
    return 0;
}

void __stdcall entrada(void) { ExitProcess((UINT)teste()); }
