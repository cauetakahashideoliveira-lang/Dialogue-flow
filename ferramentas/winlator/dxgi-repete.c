/* dxgi.dll intermediária ("dxgi-repete"): repassa tudo ao DXGI do DXVK, renomeado dxvk_dxgi.dll na mesma pasta,
   e repete a criação de swapchain quando ela falha de forma passageira com E_INVALIDARG. No Winlator com Vortek
   (Mali), a swapchain numa janela-filha falha de vez em quando e a próxima tentativa funciona; as janelas de
   plugin do Roblox Studio tentam uma vez só. Log opcional: variável DXGI_PROXY_LOG com o caminho do arquivo. */
#define COBJMACROS
#include <windows.h>
#include <dxgi1_2.h>

typedef HRESULT(WINAPI *pfnFabrica)(REFIID, void **);
typedef HRESULT(WINAPI *pfnFabrica2)(UINT, REFIID, void **);
typedef HRESULT(WINAPI *pfnDeclarar)(void);
typedef HRESULT(WINAPI *pfnDepurar1)(UINT, REFIID, void **);
typedef HRESULT(STDMETHODCALLTYPE *pfnParaJanela)(IDXGIFactory2 *, IUnknown *, HWND, const DXGI_SWAP_CHAIN_DESC1 *,
                                                  const DXGI_SWAP_CHAIN_FULLSCREEN_DESC *, IDXGIOutput *,
                                                  IDXGISwapChain1 **);
typedef HRESULT(STDMETHODCALLTYPE *pfnCriar)(IDXGIFactory2 *, IUnknown *, DXGI_SWAP_CHAIN_DESC *, IDXGISwapChain **);

static const GUID IID_Fab2 = {0x50c83a1c, 0xe072, 0x4c48, {0x87, 0xb0, 0x36, 0x30, 0xfa, 0x36, 0xa6, 0xd0}};
static HMODULE eu, real;
static pfnFabrica rFab, rFab1;
static pfnFabrica2 rFab2;
static pfnDeclarar rDeclarar;
static pfnDepurar1 rDepurar1;
static pfnParaJanela oParaJanela;
static pfnCriar oCriar;
static volatile LONG enganchado;
enum { TENTATIVAS = 8 };

static void registrar(const char *msg, HRESULT hr, int tentativa) {
    char caminho[MAX_PATH], linha[200];
    DWORD n = GetEnvironmentVariableA("DXGI_PROXY_LOG", caminho, sizeof caminho);
    if (!n || n >= sizeof caminho) return;
    HANDLE h = CreateFileA(caminho, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_ALWAYS, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return;
    int len = wsprintfA(linha, "%lu %s hr=0x%08lx tentativa=%d\r\n", GetTickCount(), msg, (unsigned long)hr, tentativa);
    DWORD escrito;
    WriteFile(h, linha, (DWORD)len, &escrito, NULL);
    CloseHandle(h);
}

static HRESULT STDMETHODCALLTYPE ganchoParaJanela(IDXGIFactory2 *f, IUnknown *dev, HWND w, const DXGI_SWAP_CHAIN_DESC1 *d,
                                                  const DXGI_SWAP_CHAIN_FULLSCREEN_DESC *tc, IDXGIOutput *saida,
                                                  IDXGISwapChain1 **sc) {
    HRESULT hr = E_FAIL;
    for (int i = 0; i < TENTATIVAS; i++) {
        hr = oParaJanela(f, dev, w, d, tc, saida, sc);
        if (hr != E_INVALIDARG || !sc || !d) {
            if (i) registrar("CreateSwapChainForHwnd depois de repetir", hr, i);
            return hr;
        }
        registrar("CreateSwapChainForHwnd falhou", hr, i);
        Sleep(25 * (i + 1));
    }
    return hr;
}

static HRESULT STDMETHODCALLTYPE ganchoCriar(IDXGIFactory2 *f, IUnknown *dev, DXGI_SWAP_CHAIN_DESC *d,
                                             IDXGISwapChain **sc) {
    HRESULT hr = E_FAIL;
    for (int i = 0; i < TENTATIVAS; i++) {
        hr = oCriar(f, dev, d, sc);
        if (hr != E_INVALIDARG || !sc || !d) {
            if (i) registrar("CreateSwapChain depois de repetir", hr, i);
            return hr;
        }
        registrar("CreateSwapChain falhou", hr, i);
        Sleep(25 * (i + 1));
    }
    return hr;
}

static void enganchar(void *obj) {
    if (!obj || enganchado) return;
    IDXGIFactory2 *f2 = NULL;
    if (FAILED(IUnknown_QueryInterface((IUnknown *)obj, &IID_Fab2, (void **)&f2)) || !f2) return;
    if (InterlockedCompareExchange(&enganchado, 1, 0) == 0) {
        IDXGIFactory2Vtbl *vt = f2->lpVtbl;
        DWORD antes;
        if (VirtualProtect(vt, sizeof *vt, PAGE_READWRITE, &antes)) {
            oParaJanela = (pfnParaJanela)vt->CreateSwapChainForHwnd;
            oCriar = (pfnCriar)vt->CreateSwapChain;
            vt->CreateSwapChainForHwnd = (void *)ganchoParaJanela;
            vt->CreateSwapChain = (void *)ganchoCriar;
            VirtualProtect(vt, sizeof *vt, antes, &antes);
            registrar("gancho instalado", S_OK, 0);
        } else {
            enganchado = 0;
        }
    }
    IDXGIFactory2_Release(f2);
}

static BOOL carregar(void) {
    if (real) return TRUE;
    char caminho[MAX_PATH];
    DWORD n = GetModuleFileNameA(eu, caminho, MAX_PATH);
    while (n && caminho[n - 1] != '\\' && caminho[n - 1] != '/') n--;
    if (!n || n + 16 >= MAX_PATH) return FALSE;
    lstrcpyA(caminho + n, "dxvk_dxgi.dll");
    HMODULE m = LoadLibraryA(caminho);
    if (!m) return FALSE;
    rFab = (pfnFabrica)GetProcAddress(m, "CreateDXGIFactory");
    rFab1 = (pfnFabrica)GetProcAddress(m, "CreateDXGIFactory1");
    rFab2 = (pfnFabrica2)GetProcAddress(m, "CreateDXGIFactory2");
    rDeclarar = (pfnDeclarar)GetProcAddress(m, "DXGIDeclareAdapterRemovalSupport");
    rDepurar1 = (pfnDepurar1)GetProcAddress(m, "DXGIGetDebugInterface1");
    real = m;
    return TRUE;
}

HRESULT WINAPI CreateDXGIFactory(REFIID riid, void **f) {
    if (!carregar() || !rFab) return E_FAIL;
    HRESULT hr = rFab(riid, f);
    if (SUCCEEDED(hr) && f) enganchar(*f);
    return hr;
}

HRESULT WINAPI CreateDXGIFactory1(REFIID riid, void **f) {
    if (!carregar() || !rFab1) return E_FAIL;
    HRESULT hr = rFab1(riid, f);
    if (SUCCEEDED(hr) && f) enganchar(*f);
    return hr;
}

HRESULT WINAPI CreateDXGIFactory2(UINT flags, REFIID riid, void **f) {
    if (!carregar() || !rFab2) return E_FAIL;
    HRESULT hr = rFab2(flags, riid, f);
    if (SUCCEEDED(hr) && f) enganchar(*f);
    return hr;
}

HRESULT WINAPI DXGIDeclareAdapterRemovalSupport(void) {
    return carregar() && rDeclarar ? rDeclarar() : S_OK;
}

HRESULT WINAPI DXGIGetDebugInterface1(UINT flags, REFIID riid, void **p) {
    return carregar() && rDepurar1 ? rDepurar1(flags, riid, p) : E_NOINTERFACE;
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD motivo, LPVOID r) {
    (void)r;
    if (motivo == DLL_PROCESS_ATTACH) {
        eu = h;
        DisableThreadLibraryCalls(h);
    }
    return TRUE;
}
