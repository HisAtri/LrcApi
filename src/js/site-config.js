const siteConfig = {
    // 站点基本信息
    site: {
        name: "LrcAPI",
        logo: "/src/img/LrcAPI-Text-Extra.png",
        github: "https://github.com/hisatri/LrcAPI",
        license: {
            name: "GNU General Public License v3.0",
            url: "https://github.com/HisAtri/LrcApi/blob/main/LICENSE"
        }
    },
    
    // 页面导航
    navigation: [
        {
            text: "回到主页",
            url: "/",
            showInFooter: true
        },
        {
            text: "致谢名单",
            url: "/acknowledgments.html",
            showInFooter: true
        }
    ],

    // 致谢页面模块配置
    acknowledgments: {
        barrage: {   // 弹幕系统
            enabled: true,
            messages: [
                "项目越来越好！",
                "加油！继续努力！",
                "很棒的项目！",
                "支持开源！",
                "希望项目能一直维护下去",
                "太赞了！",
                "非常实用的API",
                "非常好的项目，爱来自LinuxDo",
                "我是Mio，请你吃疯狂星期四",
                "Good Job！",
                "感谢开发LRCAPI",
                "真好用",
                "完美，好东西！",
                "很棒！继续加油"
            ]
        },
        financial: {   // 财务状况
            enabled: true,
            amount: -1780.64,   // 负数表示亏损，正数表示收益
            currency: '￥',      // 货币符号
            duration: 2000,     // 动画持续时间（毫秒）
        },
        supporters: {           // 赞助者名单
            enabled: true,
            data: [
                { name: 'XinLoong', amount: 10.00 },
                { name: '木羽', amount: 5.00 },
                { name: '依然不懂', amount: 5.00 },
                { name: '扑克', amount: 20.00 },
                { name: '未知', amount: 10.00 },
                { name: 'yule', amount: 10.00 },
                { name: 'Erikaze', amount: 90.00 },
                { name: 'hikaru', amount: 10.00 },
                { name: 'KawaKaze', amount: 6.66 },
                { name: 'Mio', amount: 50.00 },
                { name: '呜噜噜', amount: 50.00 }
            ]
        }
    }
};
