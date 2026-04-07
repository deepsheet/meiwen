#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分段式 HTML 格式化器：解决超长文章被截断问题
将长文章分成多个段落，分别调用 AI 格式化，最后合并
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.html_formatter import HTMLFormatter
from src.llm_client import LLMClient
from src.logger import logger


class SegmentedHTMLFormatter(HTMLFormatter):
    """分段式 HTML 格式化器"""
    
    def __init__(self, model_name=None):
        super().__init__(model_name=model_name)
        self.segment_length = 1500  # 每段约 1500 字
        # 🔴 为分段格式化创建专用的 LLM 客户端
        self.llm_client = LLMClient(model_name=model_name)
    
    def format_article_segmented(self, content, title=None):
        """
        使用分段方式格式化长文章
        
        @param {str} content - 文章内容
        @param {str} title - 文章标题
        @return {str} - 完整的 HTML
        """
        content_length = len(content)
        
        # 如果文章不太长，直接使用普通方法
        if content_length < 3000:
            logger.info(f"文章长度 {content_length}，使用普通格式化")
            return self.format_article(content, title)
        
        logger.info(f"文章长度 {content_length}，使用分段格式化模式")
        
        # 分割文章（按段落分割，保持语义完整性）
        segments = self._split_content(content)
        logger.info(f"文章已分割为 {len(segments)} 段")
        
        # 生成 HTML 头部和标题
        html_parts = []
        html_parts.append(self._generate_html_header(title))
        
        # 逐段格式化
        for i, segment in enumerate(segments, 1):
            logger.info(f"正在格式化第 {i}/{len(segments)} 段...")
            segment_html = self._format_segment(segment, i)
            html_parts.append(segment_html)
        
        # 添加 HTML 尾部
        html_parts.append(self._generate_html_footer())
        
        # 合并所有部分
        full_html = '\n'.join(html_parts)
        logger.info(f"分段格式化完成，总长度：{len(full_html)}")
        
        return full_html
    
    def _split_content(self, content):
        """
        将内容分割成多个段落，保持段落完整性
        
        @param {str} content - 原始内容
        @return {list} - 分割后的段落列表
        """
        # 首先按双换行符分割成段落
        paragraphs = content.split('\n\n')
        
        segments = []
        current_segment = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # 如果当前段落本身就很长，单独成为一段
            if para_length > self.segment_length:
                if current_segment:
                    segments.append('\n\n'.join(current_segment))
                    current_segment = []
                    current_length = 0
                segments.append(para)
            else:
                # 如果加上这个段落后不超过限制，就加入当前段
                if current_length + para_length <= self.segment_length * 1.2:  # 允许 20% 的浮动
                    current_segment.append(para)
                    current_length += para_length
                else:
                    # 否则开始新的段
                    if current_segment:
                        segments.append('\n\n'.join(current_segment))
                    current_segment = [para]
                    current_length = para_length
        
        # 添加最后一段
        if current_segment:
            segments.append('\n\n'.join(current_segment))
        
        return segments
    
    def _generate_html_header(self, title=None):
        """
        生成 HTML 头部
        
        @param {str} title - 文章标题
        @return {str} - HTML 头部
        """
        title_tag = f"<title>{title}</title>" if title else "<title>文章</title>"
        title_h1 = f"""
        <!-- 文章主标题 -->
        <header style="text-align: center; margin-bottom: 40px; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 24px; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
            <h1 style="margin: 0; color: white; font-size: 2.8rem; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">📄 {title or '文章'}</h1>
        </header>
        """ if title else ""
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {title_tag}
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
</head>
<body style="margin: 0; padding: 0; font-family: 'PingFang SC', 'Microsoft YaHei', 'SimHei', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%); color: #333; line-height: 1.6;">
    <!-- 页面主容器 -->
    <div style="max-width: 900px; margin: 0 auto; padding: 20px;">
        {title_h1}
"""
    
    def _generate_html_footer(self):
        """
        生成 HTML 尾部
        
        @return {str} - HTML 尾部
        """
        return """
    </div>
</body>
</html>"""
    
    def _format_segment(self, segment, segment_index):
        """
        格式化单个段落
        
        @param {str} segment - 段落内容
        @param {int} segment_index - 段落序号
        @return {str} - 格式化后的 HTML 片段
        """
        # 🔴 使用 LLMClient 直接格式化片段
        try:
            html_fragment = self.llm_client.format_article(segment, title=None)
            # 提取 body 内容（去掉完整的 HTML 结构）
            import re
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html_fragment, re.DOTALL | re.IGNORECASE)
            if body_match:
                html_fragment = body_match.group(1).strip()
            else:
                # 如果没有找到 body 标签，直接使用原始结果
                pass
            
            # 清理可能的 markdown 标记
            html_fragment = re.sub(r'^```html\s*', '', html_fragment)
            html_fragment = re.sub(r'```$', '', html_fragment)
            html_fragment = html_fragment.strip()
            
            return html_fragment
            
        except Exception as e:
            logger.error(f"格式化第 {segment_index} 段失败：{e}")
            # 返回纯文本作为备选
            return f"<div style='background: white; padding: 20px; margin: 20px 0; border-radius: 12px;'>{segment.replace(chr(10), '<br>')}</div>"


def main():
    """测试分段格式化"""
    # 这里可以放很长的文章
    long_article = """我就喊你们来采访我呀，我骑车水平特别高！

2006 年，湖南怀化暴雨如注。

19 岁的张雪骑着一辆破旧摩托，死死盯着前方那辆电视台采访车，油门拧到底，追了整整 100 多公里，3 个小时。

图片


雨水打得他睁不开眼，衣服早已湿透，但他不放弃。

节目组的人觉得他"不过如此"，拍完就想走。

可这个倔强的湖南少年不认命，硬是又争取到一个小时的拍摄时间。

20 年后，2026 年 3 月 28 日，葡萄牙阿尔加维国际赛车场。

世界超级摩托车锦标赛（WSBK）的赛道上，一辆中国制造的摩托车以领先第二名近 4 秒的绝对优势冲过终点线。

图片
第二天，它再次夺冠，实现双冠王。

杜卡迪、雅马哈、川崎——这些垄断赛场数十年的国际巨头，集体沉默。

"这一刻我等了 20 年……我们赢了！"

从 14 岁修车学徒到 39 岁世界冠军
1987 年，张雪出生在湖南怀化的一个山村。

14 岁那年，他背着一个破旧的背包，走进县城一家摩托车修理铺，成了一名学徒。

每天天不亮就起床开门，扫院子、擦工具、拆洗满是油污的发动机，一天干十几个小时。

指甲缝里的黑机油永远洗不干净，手上的伤口刚结痂，就又被零件划破。

别人眼里又脏又累的苦活，在他眼里却是通往梦想的阶梯。

他抱着拆下来的零件研究到深夜，甚至练就了"蒙眼组装发动机"的绝活。

省吃俭用攒下的钱，他买了一辆车龄比他还大、到处是毛病的二手摩托。

这成了他赛车梦的起点。

乡间的土路上，他反复练习特技，摔得满身淤青，车摔坏了就自己修，修好了继续练。

2 万元闯重庆：一个人的火锅是"顶级孤独"
2013 年，26 岁的张雪做出了人生中最重要的决定。

揣着仅有的 2 万元积蓄，他一个人来到重庆——这座被誉为"中国摩托之都"的城市。

没有熟人，没有资源。

那一年正月十五已过，妻子问他："都过了正月十五了，你咋还不出去啊？"

"一个男人被妻子问这句话，很伤面子。"张雪后来回忆，"我索性心一横，不管了，走出去再说。"

来到重庆后，他住进银行楼上的一家宾馆。

楼下有家自助火锅店，老板看他独自用餐，投来异样目光："你一个人来吃火锅？"

张雪回应："有问题吗？"

后来他在网上看到，一个人吃火锅被列为"顶级孤独"之一。

但孤独没有击垮他。

第二天，他找到一家做出口的工厂，拿了一款公模车进行改造。

2 万元刚好够改造一台样车。

他把改装过程发到论坛上，售价 14800 元，现场购买优惠 2000 元。

但有一个条件：必须给现金，"因为我没钱"。

30 多个车友来了，把钱给他。50 万元到手。

"然后我就拿着这 50 万把这些车全部改完，交给车友。"

随后又接了 50 单，再 50 单。

第一次创业，他挣了十几万元。

但模式很快被同行复制，"我说，完了，这个事不能干了。"

最黑暗的时刻：承认失败，从头再来
转型是痛苦的。

张雪拿 10 万元找设计公司做新车设计，但只够付定金。

设计需要一年，他盘算着，这一年，必须搞钱。

他一人身兼数职，在淘宝卖车、写文案、做图、客服、售后全包，甚至亲自操作热词出价，硬生生做到了类目第一，"连官方店铺都干不过我"。

赚回几十万元后，终于有钱开模。

但开模需预付 30% 定金，漫长的开发周期内，他继续四处"搞钱"。

新车在论坛上架，原本预估卖 50 台，结果几分钟就售罄，几天内突破 500 台。

可他没钱进货。

他建立了 QQ 群，向车友"借钱"，以一瓶机油作为利息。

有车友愿借给他 40 万元，他只借了 10 万元，"万一失败，我还得起"。

靠这种"众筹"模式，他获得了几十万元的"天使投资"。

然而，这款车卖了七八百台后，他坦然承认失败了。

"开发总共花了 100 多万元，现在开一套覆盖件就要 100 多万元，是非常不合格的开发。"

用最廉价方式开发的车，质量不好，反馈不佳，没挣钱，甚至亏损。

张雪没有逃避，而是决定从头再来。

2017 年：凯越机车诞生
2017 年，他与两位合伙人共同创立凯越机车。

短短几年时间，凯越机车成为年销量约 3 万台、年营收数亿元的头部车企。

所有人都劝他：趁着热度，多做几款走量的赚钱车型不好吗？

可张雪再次做了决定——继续自主研发大排量发动机。

他把所有身家都砸进了发动机研发里，带着十几个人的团队，吃住都在工厂，没日没夜地调试、推翻、重来。

"我对失败的包容度很高，因此从不惧怕失败。"

"想到就立刻去做，即便做错了也会及时调整，不会顾及脸面，错了就直面错误。"

2024 年：以自己之名
2024 年，张雪做出了一个让所有人震惊的决定——离开自己一手创办的凯越机车。

"本人决定辞职，去追求我的星辰大海。"他在辞职信中写道。

同年 4 月，他在重庆两江新区创立了以自己名字命名的品牌——张雪机车。

注册资本 6540 万元，正式向世界顶尖赛道发起冲击。

"只要我的产品足够优秀，能拿下所有比赛的冠军，'名字'可能就是一个顶级符号。"

但创业从来不是一帆风顺。

2025 年初，张雪机车首款车 500RR 即将发布，但在这之前的 2 月份，公司已经发不出工资。

"我就到处找人借，找朋友、同行、供应商，还找我们房东借了 100 万元，一共借了 700 万元把工资发了。"

"必须要在 3 月上市，你不上市，公司就没钱了。资金链断了，你不认栽也必须要栽。"

2025 年 3 月发布会后，车辆开始交付，公司才缓过气来。

凭借扎实的自研技术与高性价比，张雪机车一上市便引爆市场，全年销量突破 2.5 万台，跻身国产中大排量摩托第一梯队。

2026 年：世界之巅
2026 年 3 月 28 日，葡萄牙阿尔加维国际赛道。

随着冲线灯亮起，张雪机车 820RR-RS 赛车稳稳占据领先位置。

身后第二名近在咫尺，却又始终无法超越——4 秒。

在 WSBK 的顶级赛场上，这不仅仅是一个时间上的差距。

长久以来，这项赛事所使用的摩托车被杜卡迪、川崎、雅马哈等欧洲和日本品牌垄断。

如今，来自中国的品牌，硬生生在强者如林的格局中撕开了一道口子。

第二天，张雪机车再次夺冠，实现分站赛"双杀"。

领先 4 秒是什么概念？

WSBK 这种级别的比赛，一场通常在 30 分钟左右，车手之间的差距往往非常小。

大多数时候，前几名的差距是 0.5 秒以内，甚至很多比赛会在最后一圈才分出胜负，差距可能只有零点几秒。

"领先 4 秒"几乎可以理解为——不在一个维度上的胜利。

夺冠后的数据爆炸
夺冠消息瞬间引爆全网。

图片


张雪机车的抖音账号粉丝数三天涨粉超百万，达到 247.8 万。

820RR 冠军车型售价 4.38 万元，仅为进口同级车型 1/3。

夺冠后 100 小时内预售订单近 8000 台，全国订单排期已至 6 月底。

不是生意，是命
在员工眼中，张雪是出了名的"暴脾气"。

"和我一起工作的同事，我估计多多少少都被我伤到过，因为我说话从来不留情面的。"

但这份锋芒背后，是极致的专注。

"我没有别的想法，就是没有理由不干它。"

20 年来，他只专注摩托车这一件事。

这种极致专注，甚至让他不考汽车驾照，"考驾照太耗时间，我只想骑车"。

他唯一的爱好是骑摩托车，每天上下班都如此。

网友调侃他：造车不是为了挣钱，是"纯瘾大"。

张雪机车的产品哲学，可以概括为三个关键词：声浪、马力、轻量化操控。

"你选车不就是看这 3 个吗？"他反问记者。

但商业逻辑上，他却做出了"反效率"的决策：

禁止驾龄一年以内的新手购买 820RR，否则相关经销商将被重罚。

"我希望少出事故。"

他承认这会影响业绩，"至少少卖 10%。但我不要这 10%，公司也不会死。"

这一切，都来自他对摩托车的认知：

不是生意，是命。

被平视的尊严
夺冠后，张雪在采访中说了一段话，让很多人动容：

"早年去国际赛场时，别人就是用不屑的眼光看你的。夺冠后，别人是平视着和你说话。"

被问及其他品牌有没有来祝贺，他说："围场里面大家其实还是会祝贺的。"

这不仅是个人受尊重程度的变化，更是产业地位的重塑。

张雪机车的成功，背后是中国制造的深厚底蕴。

目前，重庆两江新区正规划打造高端摩托车产业园，为张雪机车提供近 200 亩生产基地。

"只要是车上的任何一个零件，哪怕是摩托 GP 和 F1 车上的任何一个零件，只要有图纸到中国，100% 能做出来，而且绝对不比欧日美差。"

"中国摩托车产业缺的不是制造能力，而是'经验库'。遇到一个问题，整个团队扑上去啃。一天啃不下来，就一周；一周啃不下来，一个月总能啃下来。"

下一个 20 年
夺冠后的张雪，没有停下脚步。

"一家企业能成功，往往就在那几年，做不成功你给他 20 年还是做不成功。"

他给张雪机车划定的窗口期是 3 年，"从今天开始算，最多 3 年，行就行，不行就没机会了。"

目前，张雪机车仍面临产能瓶颈。

500RR 累计欠单约 3000 台，820 系列欠单约 3000 台。

"原来一天产 100 多台，现在能到 200 多台，第二条产线也在建了。"

但更大的梦想已经展开：

"未来 5 年，我们会'吃掉'国际这些所谓大牌 50% 以上的大排量市场份额。"

这个看似激进的目标，是他给自己，也给中国摩托车产业下的"战书"。

而这份野心，正从赛场开始落地：

下一步，张雪机车将参加 2026 年 9 月上海站的 MXGP 赛事，并已开始筹备达喀尔拉力赛。

"有生之年，我们要去 MotoGP（世界摩托车锦标赛）。"

张雪对媒体记者说，又像在自己确认。

从湖南怀化到葡萄牙阿尔加维
从湖南怀化的土坯房，到葡萄牙阿尔加维的领奖台，张雪走了 20 年。

这条路，他一个人修车、一个人骑车、一个人画图、一个人发帖、一个人从零开始造发动机。

如今，他的名字被刻进了世界顶级赛事的冠军榜。

那个在雨中追车的少年，终于让全世界看到了中国摩托。

而这一切，才刚刚开始。

"有时候你做一件事，不是奔着结果，而是因为热爱去做的，可能结果真的不一样。"

——张雪

图片


【互动话题】
你身边有没有像张雪这样"死磕"的人？
如果给你 2 万元，你会选择什么样的创业？
中国制造还有哪些领域需要这样的"破局者"？
欢迎在评论区分享你的故事和观点！

2026 年 4 月 1 日记



转发这条内容，让更多人看到中国制造业的崛起！
--------"""
    
    formatter = SegmentedHTMLFormatter()
    
    print("=" * 80)
    print("测试分段式 HTML 格式化")
    print("=" * 80)
    print(f"\n原文长度：{len(long_article)} 字")
    
    try:
        result = formatter.format_article_segmented(long_article, "我就喊你们来采访我呀，我骑车水平特别高！")
        
        print(f"\n✅ 格式化成功！HTML 长度：{len(result)}")
        
        # 检查关键内容
        key_phrases = [
            "楼下有家自助火锅店，老板看他独自用餐",
            "不是生意，是命",
            "被平视的尊严",
            "下一个 20 年",
            "互动话题"
        ]
        
        print("\n检查完整性:")
        for phrase in key_phrases:
            status = "✅" if phrase in result else "❌"
            print(f"{status} {phrase}")
        
        # 保存
        with open('logs/segmented_test.html', 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"\n✅ HTML 已保存到：logs/segmented_test.html")
        
    except Exception as e:
        print(f"\n❌ 失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
