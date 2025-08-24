#!/usr/bin/env python3
"""Oracle Network Test CLI - 命令行版本"""

import asyncio
import json
import sys
import argparse
from typing import Optional, List, Dict, Any
from datetime import datetime
import csv
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.panel import Panel
from rich import box

from src import ORACLE_SERVERS, NetworkTester, get_public_ip

console = Console()


class CLITester:
    """CLI测试器"""
    
    def __init__(self):
        self.tester = NetworkTester()
        self.results = []
        self.country_map = {
            '美国': '🇺🇸',
            '加拿大': '🇨🇦', 
            '巴西': '🇧🇷',
            '智利': '🇨🇱',
            '英国': '🇬🇧',
            '德国': '🇩🇪',
            '瑞士': '🇨🇭',
            '荷兰': '🇳🇱',
            '法国': '🇫🇷',
            '沙特阿拉伯': '🇸🇦',
            '阿联酋': '🇦🇪',
            '以色列': '🇮🇱',
            '南非': '🇿🇦',
            '印度': '🇮🇳',
            '新加坡': '🇸🇬',
            '澳大利亚': '🇦🇺',
            '日本': '🇯🇵',
            '韩国': '🇰🇷'
        }
    
    def get_country_emoji(self, server_name: str) -> str:
        """获取国家emoji"""
        for country in self.country_map:
            if country in server_name:
                return self.country_map[country]
        return '🌍'
    
    def create_banner_panel(self):
        """创建横幅面板"""
        banner_text = "[bold cyan]Oracle Cloud Network Test Tool - CLI v2.0[/bold cyan]\n[dim cyan]Test 24 Global Data Centers[/dim cyan]"
        
        return Panel(
            banner_text,
            border_style="cyan",
            box=box.DOUBLE,
            padding=(0, 1),
            width=console.size.width
        )
    
    def create_ip_info_panel(self, ip_info=None):
        """创建IP信息面板"""
        if ip_info is None:
            ip_info = {}
        
        # IPv4和IPv6显示
        ipv4_text = f"🌐 IPv4: {ip_info.get('ipv4', '未检测到')}"
        ipv6_text = f"🌍 IPv6: {ip_info.get('ipv6', '未检测到')}"
        location_text = f"📍 位置: {ip_info.get('city', '未知')}"
        region_text = f"🗺️ 区域: {ip_info.get('region', '未知')}"
        country_text = f"🌏 国家: {ip_info.get('country', '未知')}"
        isp_text = f"🏢 运营商: {ip_info.get('isp', '未知运营商')}"
        
        return Panel(
            f"{ipv4_text}\n{ipv6_text}\n{location_text}\n{region_text}\n{country_text}\n{isp_text}\n\n"
            f"[yellow]⚠️ 如果显示的不是您的本地IP地址，请在测试前关闭网络代理/VPN以获得准确的测试结果[/yellow]",
            title="📊 网络信息",
            border_style="green",
            width=console.size.width
        )
    
    async def run_full_test_with_live_display(self, regions: Optional[List[str]] = None, show_banner: bool = True, show_ip: bool = True):
        """完整的测试流程，在Live中显示所有内容"""
        servers_to_test = {}
        
        # 筛选要测试的服务器
        if regions:
            for name, info in ORACLE_SERVERS.items():
                if info['region'] in regions or name in regions:
                    servers_to_test[name] = info
        else:
            servers_to_test = ORACLE_SERVERS
        
        if not servers_to_test:
            console.print("[red]No servers match the specified regions[/red]")
            return []
        
        # 预先获取IP信息，避免在Live更新中重复请求
        ip_info = {}
        if show_ip:
            console.print("[dim]正在获取网络信息...[/dim]")
            try:
                ip_info = get_public_ip()
                # 临时调试输出
                if all(v == "Unknown" for k, v in ip_info.items() if k in ["city", "region", "country", "isp"]):
                    console.print(f"[yellow]调试信息: 网络信息获取失败，IP: {ip_info.get('ipv4', 'Unknown')}[/yellow]")
            except Exception as e:
                console.print(f"[red]网络信息获取出错: {e}[/red]")
                ip_info = {}
        
        results = []
        
        # 创建实时更新的表格
        def create_live_table():
            table = Table(
                title=f"🌍 Oracle Cloud Network Test Results ({len(results)}/{len(servers_to_test)})",
                box=box.SIMPLE_HEAD,
                show_header=True,
                header_style="bold cyan",
                show_lines=False,
                width=console.size.width
            )
            
            table.add_column("Rank", style="cyan")
            table.add_column("Location", style="white")
            table.add_column("Region", style="dim")
            table.add_column("Latency", justify="right")
            table.add_column("Packet Loss", justify="right")
            table.add_column("Connection", justify="right")
            table.add_column("Jitter", justify="right")
            table.add_column("Score", justify="right")
            
            # 按评分排序
            sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
            
            for idx, result in enumerate(sorted_results, 1):
                # 根据评分设置颜色
                if result['score'] >= 90:
                    score_color = "green"
                elif result['score'] >= 70:
                    score_color = "yellow"
                elif result['score'] >= 50:
                    score_color = "orange1"
                else:
                    score_color = "red"
                
                # 根据延迟设置颜色
                if result['latency'] < 50:
                    latency_color = "green"
                elif result['latency'] < 100:
                    latency_color = "yellow"
                elif result['latency'] < 200:
                    latency_color = "orange1"
                else:
                    latency_color = "red"
                
                country_emoji = self.get_country_emoji(result['name'])
                table.add_row(
                    str(idx),
                    f"{country_emoji} {result['name']}",
                    result['region'],
                    f"[{latency_color}]{result['latency']:.1f} ms[/{latency_color}]",
                    f"{result['packet_loss']:.1f}%",
                    f"{result['connection_time']:.1f} ms",
                    f"{result['jitter']:.1f} ms",
                    f"[{score_color}]{result['score']:.1f}[/{score_color}]"
                )
            
            # 为未完成的测试添加占位符
            remaining_count = len(servers_to_test) - len(results)
            for i in range(remaining_count):
                table.add_row(
                    str(len(results) + i + 1),
                    "[dim]Testing...[/dim]",
                    "[dim]---[/dim]",
                    "[dim]--- ms[/dim]",
                    "[dim]---%[/dim]",
                    "[dim]--- ms[/dim]",
                    "[dim]--- ms[/dim]",
                    "[dim]---[/dim]"
                )
            
            return table
        
        # 创建进度条
        def create_progress_panel():
            from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn, SpinnerColumn
            
            if len(results) == 0:
                progress_percentage = 0
            else:
                progress_percentage = len(results) / len(servers_to_test) * 100
            
            # 创建简化的进度条组件（无Spinner减少卡顿）
            progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(
                    bar_width=None,  # 自动宽度
                    style="cyan",
                    complete_style="green",
                    finished_style="bright_green"
                ),
                MofNCompleteColumn(),
                TextColumn("•"),
                TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
                expand=True
            )
            
            # 添加任务
            if len(results) == len(servers_to_test):
                task_description = "✅ Testing Complete"
                task = progress.add_task(
                    task_description,
                    total=len(servers_to_test),
                    completed=len(results)
                )
            else:
                task_description = "🌍 Testing Oracle Cloud Servers"
                task = progress.add_task(
                    task_description,
                    total=len(servers_to_test),
                    completed=len(results)
                )
            
            return Panel(
                progress,
                border_style="bright_blue",
                title="⚡ Network Testing Progress",
                width=console.size.width,
                padding=(0, 1)
            )
        
        # 创建完整页面布局
        def create_full_display():
            from rich.layout import Layout
            
            layout = Layout()
            
            # 根据参数决定显示什么
            layout_parts = []
            
            if show_banner:
                layout_parts.append(Layout(self.create_banner_panel(), size=5))
            
            if show_ip:
                layout_parts.append(Layout(self.create_ip_info_panel(ip_info), size=10))
            
            layout_parts.extend([
                Layout(create_progress_panel(), minimum_size=3, ratio=0),
                Layout(create_live_table(), ratio=1)
            ])
            
            layout.split_column(*layout_parts)
            return layout
        
        # 使用Live显示完整界面，降低刷新频率避免卡顿
        with Live(create_full_display(), console=console, refresh_per_second=1) as live:
            
            async def update_display(result):
                results.append(result)
                # 进一步减少更新频率：每5个结果或完成时才更新
                if len(results) % 5 == 0 or len(results) == len(servers_to_test) or len(results) == 1:
                    live.update(create_full_display())
            
            # 运行测试
            await self.tester.test_all_servers(servers_to_test, update_display)
        
        return results
    
    async def test_with_progress(self, regions: Optional[List[str]] = None):
        """保持兼容性的测试方法"""
        return await self.run_full_test_with_live_display(regions, show_banner=False, show_ip=False)
    
    def display_results_table(self, results: List[Dict[str, Any]], top_n: Optional[int] = None):
        """显示结果表格"""
        # 按评分排序
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        if top_n:
            results = results[:top_n]
        
        table = Table(
            title="Test Results",
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style="bold cyan",
            show_lines=False
        )
        
        table.add_column("Rank", style="cyan")
        table.add_column("Location", style="white")
        table.add_column("Region", style="dim")
        table.add_column("Latency", justify="right")
        table.add_column("Packet Loss", justify="right")
        table.add_column("Connection", justify="right")
        table.add_column("Jitter", justify="right")
        table.add_column("Score", justify="right")
        
        for idx, result in enumerate(results, 1):
            # 根据评分设置颜色
            if result['score'] >= 90:
                score_color = "green"
            elif result['score'] >= 70:
                score_color = "yellow"
            elif result['score'] >= 50:
                score_color = "orange1"
            else:
                score_color = "red"
            
            # 根据延迟设置颜色
            if result['latency'] < 50:
                latency_color = "green"
            elif result['latency'] < 100:
                latency_color = "yellow"
            elif result['latency'] < 200:
                latency_color = "orange1"
            else:
                latency_color = "red"
            
            country_emoji = self.get_country_emoji(result['name'])
            table.add_row(
                str(idx),
                f"{country_emoji} {result['name']}",
                result['region'],
                f"[{latency_color}]{result['latency']:.1f} ms[/{latency_color}]",
                f"{result['packet_loss']:.1f}%",
                f"{result['connection_time']:.1f} ms",
                f"{result['jitter']:.1f} ms",
                f"[{score_color}]{result['score']:.1f}[/{score_color}]"
            )
        
        console.print(table, justify="center")
    
    def export_results(self, results: List[Dict[str, Any]], format: str, output: str):
        """导出测试结果"""
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        if format == 'json':
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            with open(output, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        
        elif format == 'markdown':
            with open(output, 'w', encoding='utf-8') as f:
                f.write("# Oracle Cloud Network Test Results\n\n")
                f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Summary\n\n")
                f.write(f"- Total Servers Tested: {len(results)}\n")
                f.write(f"- Best Server: {results[0]['name']} (Score: {results[0]['score']})\n")
                f.write(f"- Worst Server: {results[-1]['name']} (Score: {results[-1]['score']})\n\n")
                
                f.write("## Detailed Results\n\n")
                f.write("| Rank | Location | Region | Latency (ms) | Packet Loss | Connection (ms) | Score |\n")
                f.write("|------|----------|--------|-------------|-------------|-----------------|-------|\n")
                
                for idx, r in enumerate(results, 1):
                    f.write(f"| {idx} | {r['name']} | {r['region']} | "
                           f"{r['latency']:.1f} | {r['packet_loss']:.1f}% | "
                           f"{r['connection_time']:.1f} | {r['score']:.1f} |\n")
        
        console.print(f"[green]Results exported to {output}[/green]")
    
    def recommend_best_region(self, results: List[Dict[str, Any]], use_case: str) -> Dict[str, Any]:
        """根据使用场景推荐最佳区域"""
        recommendations = {
            "general": lambda r: r['score'],  # 综合评分
            "gaming": lambda r: (100 - r['latency']) * 0.6 + (100 - r['jitter']) * 0.4,  # 低延迟低抖动
            "streaming": lambda r: (100 - r['packet_loss']) * 0.5 + (100 - r['jitter']) * 0.5,  # 低丢包低抖动
            "download": lambda r: (100 - r['connection_time']/10),  # 快速连接
        }
        
        if use_case not in recommendations:
            use_case = "general"
        
        scorer = recommendations[use_case]
        best = max(results, key=scorer)
        
        panel = Panel(
            f"[bold]Best Region for {use_case.upper()}:[/bold]\n"
            f"📍 {best['name']}\n"
            f"🌐 Region: {best['region']}\n"
            f"⚡ Latency: {best['latency']:.1f}ms\n"
            f"📊 Score: {best['score']:.1f}\n\n"
            f"[dim]This recommendation is based on your network conditions[/dim]",
            title="Recommendation",
            border_style="green",
            box=box.DOUBLE
        )
        console.print(panel, justify="center")
        
        return best


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Oracle Cloud Network Test CLI Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Test all regions
  %(prog)s --regions us-ashburn-1    # Test specific region
  %(prog)s --top 5                   # Show top 5 results
  %(prog)s --export json -o results.json   # Export as JSON
  %(prog)s --recommend gaming        # Get recommendation for gaming
        """
    )
    
    parser.add_argument(
        '--regions', '-r',
        nargs='+',
        help='Specific regions to test (e.g., us-ashburn-1 ap-tokyo-1)'
    )
    
    parser.add_argument(
        '--top', '-t',
        type=int,
        help='Show only top N results'
    )
    
    parser.add_argument(
        '--export', '-e',
        choices=['json', 'csv', 'markdown'],
        help='Export format'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (required with --export)'
    )
    
    parser.add_argument(
        '--recommend',
        choices=['general', 'gaming', 'streaming', 'download'],
        help='Get recommendation for specific use case'
    )
    
    parser.add_argument(
        '--no-ip',
        action='store_true',
        help='Skip IP information display'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode (minimal output)'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.export and not args.output:
        console.print("[red]Error: --output is required when using --export[/red]")
        sys.exit(1)
    
    # 创建测试器
    cli = CLITester()
    
    # 运行测试
    try:
        # 使用完整的Live显示模式，或者简化模式
        if args.quiet:
            results = asyncio.run(cli.test_with_progress(args.regions))
        else:
            results = asyncio.run(cli.run_full_test_with_live_display(
                regions=args.regions,
                show_banner=True,
                show_ip=not args.no_ip
            ))
        
        if not results:
            console.print("[red]No test results available[/red]")
            sys.exit(1)
        
        # 测试完成后显示完整结果（如果需要top N或者quiet模式）
        if args.top and not args.quiet:
            console.print("\n")
            console.print(f"[bold cyan]Top {args.top} Results:[/bold cyan]", justify="center")
            cli.display_results_table(results, args.top)
        
        # 导出结果
        if args.export:
            cli.export_results(results, args.export, args.output)
        
        # 推荐
        if args.recommend:
            console.print("\n")
            cli.recommend_best_region(results, args.recommend)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()