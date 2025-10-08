const modules = import.meta.glob('./features/*.js', { eager: true });

document.addEventListener('DOMContentLoaded', () => {
  Object.values(modules).forEach(module => {
    if (module.init && typeof module.init === 'function') {
      module.init();
    }
  });
});
