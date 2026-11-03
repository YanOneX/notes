import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 站点配置
 *
 * 需要你亲自改的地方只有：
 *   1. pageTitle —— 站点名（浏览器标签、左上角标题）
 *   2. baseUrl   —— 站点地址。默认按 GitHub 仓库自动推算：Actions 里读
 *                   GITHUB_REPOSITORY，本地构建退回占位值；绑定自定义域名
 *                   或想手动指定时，设环境变量 QUARTZ_BASE_URL。
 *   3. Footer 里的 GitHub 链接（见 quartz.layout.ts）
 */

const repoFull = process.env.GITHUB_REPOSITORY // 形如 "owner/repo"，Actions 中自动注入
const [repoOwner, repoName] = (repoFull ?? "YanOneX/notes").split("/")
const ownerLower = (repoOwner ?? "yanonex").toLowerCase()
const repoLower = (repoName ?? "notes").toLowerCase()

// 仓库名为 owner.github.io 时是「用户站点」，URL 不带仓库名；否则是「项目站点」
const inferredBaseUrl =
  repoLower === `${ownerLower}.github.io`
    ? `${ownerLower}.github.io`
    : `${ownerLower}.github.io/${repoLower}`

const config: QuartzConfig = {
  configuration: {
    pageTitle: "课程笔记",
    pageTitleSuffix: " · 课程笔记",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-CN",
    baseUrl: process.env.QUARTZ_BASE_URL ?? inferredBaseUrl,
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Noto Sans SC",
        body: "Noto Sans SC",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#faf8f8",
          lightgray: "#e5e5e5",
          gray: "#b8b8b8",
          darkgray: "#4e4e4e",
          dark: "#2b2b2b",
          secondary: "#284b63",
          tertiary: "#84a59d",
          highlight: "rgba(143, 159, 169, 0.15)",
          textHighlight: "#fff23688",
        },
        darkMode: {
          light: "#161618",
          lightgray: "#393639",
          gray: "#646464",
          darkgray: "#d4d4d4",
          dark: "#ebebec",
          secondary: "#7b97aa",
          tertiary: "#84a59d",
          highlight: "rgba(143, 159, 169, 0.15)",
          textHighlight: "#b3aa0288",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      // mermaid 图、Obsidian [[双链]]、callout 都由它处理
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false, mermaid: true }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // 社交分享图（OG image）默认字体渲染不了中文标题，还明显拖慢构建，先关掉
      // Plugin.CustomOgImages(),
    ],
  },
}

export default config
