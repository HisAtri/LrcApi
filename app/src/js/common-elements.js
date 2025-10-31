class CommonElements {
    constructor(config) {
        this.config = config;
    }

    // 渲染页头
    renderHeader() {
        const header = document.createElement('header');
        header.innerHTML = `
            <div class="logo-container" style="cursor: pointer">
                <img src="${this.config.site.logo}" alt="${this.config.site.name} Logo" class="logo">
                <span class="project-name">${this.config.site.name}</span>
            </div>
            <div class="github-link">
                <a href="${this.config.site.github}" class="github-button">
                    <svg height="20" viewBox="0 0 16 16" width="20" class="github-icon">
                        <path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                    </svg>
                    GitHub
                </a>
            </div>
        `;

        // 添加点击事件监听器
        const logoContainer = header.querySelector('.logo-container');
        logoContainer.addEventListener('click', () => {
            window.location.href = '/';
        });

        return header;
    }

    // 渲染页脚
    renderFooter() {
        const footer = document.createElement('footer');
        const footerLinks = this.config.navigation
            .filter(item => item.showInFooter)
            .map(item => `<a href="${item.url}">${item.text}</a>`)
            .join(' | ');

        footer.innerHTML = `
            <p class="license-text">
                本项目基于 <a href="${this.config.site.license.url}" target="_blank" style="color: gray; text-decoration: none;">
                    ${this.config.site.license.name}
                </a> 开源协议发布 | ${footerLinks}
            </p>
        `;
        return footer;
    }

    // 初始化页面公共元素
    init() {
        // 替换页头
        const existingHeader = document.querySelector('header');
        if (existingHeader) {
            existingHeader.replaceWith(this.renderHeader());
        }

        // 替换页脚
        const existingFooter = document.querySelector('footer');
        if (existingFooter) {
            existingFooter.replaceWith(this.renderFooter());
        }
    }
}

// 当DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    const commonElements = new CommonElements(siteConfig);
    commonElements.init();
}); 