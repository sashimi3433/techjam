let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    // インストールプロンプトを表示
    showInstallPrompt();
});

function showInstallPrompt() {
    if (deferredPrompt) {
        // プロンプトを表示
        deferredPrompt.prompt();

        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('PWAがインストールされました');
            }
            deferredPrompt = null;
        });
    }
}