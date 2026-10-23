import json,html,re,pathlib,hashlib
R=pathlib.Path(__file__).resolve().parent
events=json.loads((R/'source-content.json').read_text(encoding='utf8'))
# Boundaries follow the instructor's narrative, never remove source lines.
sections=[
(1,'课程总览','导读'),(3,'课后视频清单','导读'),(4,'这节课的问题','导读'),(11,'“它”指谁？','文字与编号'),
(16,'字符编码：先让文字能被保存','文字与编号'),(21,'把一句话分成小块','文字与编号'),(25,'四个概念，先走一遍','文字与编号'),
(31,'分词：拆开的过程','文字与编号'),(39,'Token：拆出来的东西','文字与编号'),(49,'切分粒度与词性','文字与编号'),
(59,'词表：小块与编号的对照表','文字与编号'),(65,'一组具体的 Token ID','文字与编号'),(73,'查词表，得到编号','文字与编号'),
(81,'同一词表，同一个编号','文字与编号'),(92,'编号只负责区分身份','文字与编号'),
(99,'Embedding：从编号到向量','向量与 Embedding'),(106,'只有编号，为什么还不够？','向量与 Embedding'),
(111,'给每个词一份更丰富的表示','向量与 Embedding'),(116,'向量：一张数字资料卡','向量与 Embedding'),(120,'Embedding 具体做什么？','向量与 Embedding'),
(124,'学号与身高、体重','向量与 Embedding'),(131,'猫、狗、汽车的六句话','共现与真实词向量'),
(144,'固定规则，固定顺序','共现与真实词向量'),(151,'逐个数出“猫”的数字','共现与真实词向量'),
(165,'把一行统计结果写成向量','共现与真实词向量'),(176,'顺序可以改，但必须一起改','共现与真实词向量'),
(186,'为什么这样的数字有用？','共现与真实词向量'),(193,'真实案例：GloVe 词向量','共现与真实词向量'),
(206,'0.45281 究竟是什么意思？','共现与真实词向量'),(209,'训练：让数字表达规律','共现与真实词向量'),
(217,'怎样知道整组数字有用？','共现与真实词向量'),(223,'每一维不一定有人类标签','共现与真实词向量'),
(234,'再理解一次 Embedding','共现与真实词向量'),(239,'把 Token ID 与向量接起来','共现与真实词向量'),
(251,'编号负责找，向量参与算','共现与真实词向量'),(256,'回到“小猫”和“沙发”','向量与点积'),
(260,'两个位置，表示两类线索','向量与点积'),(267,'二维向量在案例里有什么用？','向量与点积'),
(273,'点积：按当前标准打分','向量与点积'),(279,'先给“小猫”打分','向量与点积'),(286,'再给“沙发”打分','向量与点积'),
(291,'加权求和：把信息合起来','加权求和'),(298,'参考谁，取决于当前问题','加权求和'),
(304,'为什么需要具体的比例？','加权求和'),(307,'先认识“比例换算器”','加权求和'),(310,'73% 与 27% 从哪里来？','加权求和'),
(319,'内容与比例，是两件事','加权求和'),(323,'小猫：每一项都取 73%','加权求和'),(331,'沙发：每一项都取 27%','加权求和'),
(338,'求和：把同类线索合起来','加权求和'),(343,'同一个权重，不同的原始内容','加权求和'),
(347,'相乘以后，才知道实际贡献','加权求和'),(350,'完整回顾：先乘，再加','加权求和'),
(354,'[0.73, 0.27] 是什么？','加权求和'),(360,'点积与加权求和的区别','加权求和'),(364,'把整个案例再串起来','加权求和'),
(372,'这个过程叫注意力机制','Q、K、V 与注意力'),(375,'Q：当前用来发起匹配的信息','Q、K、V 与注意力'),
(383,'K：供我们判断匹配程度的信息','Q、K、V 与注意力'),(388,'Q 与 K 计算匹配分数','Q、K、V 与注意力'),
(391,'比例换算器的名字：softmax','Q、K、V 与注意力'),(394,'softmax 只处理前面的分数','Q、K、V 与注意力'),
(399,'注意力权重：汇总时要乘的数','Q、K、V 与注意力'),(402,'V：真正参与汇总的内容','Q、K、V 与注意力'),
(407,'K 与 V：两份数据，两种用途','Q、K、V 与注意力'),(410,'点积这一步，只拿 Q 和 K','Q、K、V 与注意力'),
(413,'由匹配分数，得到参考比例','Q、K、V 与注意力'),(417,'最后把权重用在 V 上','Q、K、V 与注意力')]
starts={f'line-{n}':(t,c) for n,t,c in sections}
slides=[]; current=None
for e in events:
 if e['id'] in starts:
  t,c=starts[e['id']]; current={'title':t,'chapter':c,'events':[]};slides.append(current)
 current['events'].append(e)

formula={
'figure-9-0':'[1, 0] · [1, 0] = 1 × 1 + 0 × 0 = 1',
'figure-9-1':'[1, 0] · [0, 1] = 1 × 0 + 0 × 1 = 0',
'figure-10-1':'73% × [1, 0] = [0.73, 0]',
'figure-11-0':'27% × [0, 1] = [0, 0.27]',
'figure-11-1':'73% × [2, 0] = [1.46, 0]',
'figure-11-2':'73% × [1, 0] = [0.73, 0]\n27% × [0, 1] = [0, 0.27]',
'figure-11-3':'[0.73, 0] + [0, 0.27] = [0.73, 0.27]',
'figure-12-1':'Q = [1, 0]', 'figure-14-0':'Q = [1, 0]',
'figure-14-1':'[1, 0] · [1, 2] = 1 × 1 + 0 × 2 = 1',
'figure-14-2':'[1, 0] · [0, 3] = 1 × 0 + 0 × 3 = 0',
'figure-14-3':'0.73[1, 0] + 0.27[0, 1] = [0.73, 0.27]',
'figure-13-2':'匹配分数 → softmax：比例换算器 → 参考比例',
'figure-10-0':'小猫 1 分，沙发 0 分 → 比例换算器 → 小猫约 73%，沙发约 27%'
}
focus={20,37,43,54,56,63,66,80,90,91,92,97,103,110,117,121,130,145,173,183,184,190,197,216,221,231,232,235,252,255,268,270,272,284,289,290,303,304,305,306,308,316,317,322,325,333,342,343,346,347,349,358,359,362,363,373,379,387,395,398,400,401,407,409,414,416,419}
keyterms=['上下文信息汇总','对应位置相乘','按固定顺序','共同发挥作用','不是最终答案','不是真实模型的结果','匹配分数','注意力权重','比例换算器','加权求和','共现计数向量','Token ID','Embedding','Tokenizer','Vocabulary','softmax','GloVe','字符编码','二维向量','三维向量']
rx=re.compile('|'.join(map(re.escape,keyterms)))
def rich(t):
 # Keep source wording; Markdown emphasis markers are presentation syntax.
 t=html.escape(t).replace('**','')
 return rx.sub(lambda m:'<strong>'+m.group(0)+'</strong>',t)

def render(items):
 out=[]; i=0
 while i<len(items):
  e=items[i]
  if e['type']=='figure':
   f=formula.get(e['id'])
   if f:out.append('<div class="formula" aria-label="公式清晰排版">'+html.escape(f).replace('\n','<br>')+'</div>')
   alt=('公式原图：'+f) if f else '讲义原图，PDF 第 '+str(e['page'])+' 页'
   out.append(f'<figure data-source="{e["id"]}" class="{"equation-original" if f else "table-original"}"><button class="image-button" data-image="{e["src"]}" data-caption="{html.escape(alt,quote=True)}" aria-label="放大{html.escape(alt,quote=True)}"><img src="{e["src"]}" width="{e["width"]}" height="{e["height"]}" loading="lazy" alt="{html.escape(alt,quote=True)}"></button><figcaption>{"原图" if f else "原讲义图片"} · 点击放大</figcaption></figure>')
   i+=1;continue
  group=[e];i+=1
  while i<len(items) and items[i]['type']=='text' and items[i]['page']==group[-1]['page'] and items[i]['top']-group[-1]['bottom']<10 and not re.match(r'^(\d+\s|•|代码块)',items[i]['text']):
   group.append(items[i]);i+=1
  content=''.join(x['text'] for x in group)
  ids=' '.join(x['id'] for x in group)
  isfocus=any(int(x['id'].split('-')[1]) in focus for x in group)
  cls='focus' if isfocus else ('subheading' if e['bold'] and len(content)<65 else 'paragraph')
  if re.match(r'^\d+\s',content) or content=='代码块' or '代码块' in content:cls+=' example-line'
  if content.startswith('•'):cls+=' bullet'
  out.append(f'<p class="{cls}" data-source="{ids}">{rich(content)}</p>')
 return '\n'.join(out)

articles=[]
articles.append('''<section class="slide cover" data-title="从文字开始，理解一次注意力计算" data-chapter="首页"><div class="cover-meta">FOUNDATION OF AI　/　10.23</div><h1>从文字开始，<br>理解一次<span>注意力计算</span></h1><p class="cover-line">第一堂课 · 完整阅读讲义</p><p class="cover-question">“小猫跳上沙发，因为它……”<br>这里的“它”，指谁？</p><div class="cover-bottom"><p><b>方正 Felix</b><br>EDUHK AIDCEC 研究助理</p><button class="primary" data-go="2">开始阅读 <span>→</span></button></div></section>''')
articles.append('''<section class="slide bio" data-title="主讲人：方正 Felix" data-chapter="主讲人"><header><span class="eyebrow">主讲人</span><h2>方正 <em>Felix</em></h2></header><div class="slide-body"><p class="bio-role">EDUHK AIDCEC 研究助理</p><div class="bio-grid"><div><h3>教育背景</h3><p>香港理工大学<br><strong>计算机与人工智能博士（在读）</strong></p><p>EDUHK<br><strong>AIEP 硕士</strong></p><p>中国石油大学（北京）<br><strong>石油工程学士</strong></p></div><div><h3>工作经历</h3><p>腾讯<br><strong>数据工程师</strong></p><p>学而思九章大模型 MathGPT<br><strong>推理优化算法工程师</strong></p></div></div></div></section>''')
for si,s in enumerate(slides):
 pages=sorted(set(e['page'] for e in s['events']))
 source=' '.join(f'<button class="source-link" data-image="assets/original-page-{p:02}.png" data-caption="PDF 第 {p} 页'+('（第一堂课部分）' if p==14 else '')+f'">原页 {p}</button>' for p in pages)
 body=render(s['events'])
 # Editorial annotations supplement (never replace) the source text.
 extra=''
 if any(e['id'] in ['line-27','line-98'] for e in s['events']):extra='<aside class="editor-note">阅读提示：这行原文的“词表”和“Token”位置写反了。应理解为：分词（拆句子）→ Token（得到小块）→ 查词表 → Token ID（得到编号）。原文仍完整保留在上方。</aside>'
 if any(e['id']=='line-315' for e in s['events']):extra+='<aside class="editor-note">阅读提示：这里用“主体与场景”解释信息汇总的用途。保留沙发信息不是所有任务的硬性要求。</aside>'
 if any(e['id']=='line-383' for e in s['events']):extra+='<aside class="editor-note">沿用后文的说明：动物/家具标签用于教学 V。这里 K 只是匹配用的数字，不把 K 的两个维度继续命名为动物/家具。</aside>'
 if any(e['id']=='figure-10-0' for e in s['events']):extra+='<aside class="editor-note">原 PDF 的红字是未渲染的公式源码。上方提供了相同数字与含义的清晰排版，原图仍保留。</aside>'
 articles.append(f'<section class="slide" data-title="{html.escape(s["title"],quote=True)}" data-chapter="{s["chapter"]}"><header><span class="eyebrow">{s["chapter"]}</span><h2>{s["title"]}</h2></header><div class="slide-body">{body}{extra}</div><footer class="slide-footer">{source}<span class="scroll-hint" hidden>本页还有内容，向下阅读 ↓</span></footer></section>')
articles.append('''<section class="slide" data-title="视频链接与课后阅读" data-chapter="课后资源"><header><span class="eyebrow">课后资源</span><h2>视频链接与课后阅读</h2></header><div class="slide-body resource-list"><a href="http://xhslink.com/m/lcIXwUKMkE" target="_blank" rel="noopener"><b>文字如何变成数字</b><span>1 分 30 秒 · 复习编号与向量 ↗</span></a><a href="http://xhslink.com/m/7LwgcyTZRsg" target="_blank" rel="noopener"><b>Transformer 注意力机制详解</b><span>11 分 44 秒 · 复习 Q/K 匹配与 V 加权汇总 ↗</span></a><a href="http://xhslink.com/m/8NvSu7LSeyu" target="_blank" rel="noopener"><b>Transformer 统治 AI 与神经网络的进化</b><span>11 分 11 秒 · 课外拓展 ↗</span></a><a href="http://xhslink.com/m/6gm7NNdoj2a" target="_blank" rel="noopener"><b>大模型如何学会与人聊天</b><span>12 分 24 秒 · 课外拓展 ↗</span></a><a href="https://nlp.stanford.edu/projects/glove/" target="_blank" rel="noopener"><b>斯坦福 GloVe 官方介绍</b><span>阅读词向量的训练思路 ↗</span></a></div></section>''')
template=(R/'template.html').read_text(encoding='utf8')
(R/'index.html').write_text(template.replace('<!-- CONTENT -->','\n'.join(articles)),encoding='utf8')
flat=[e['id'] for s in slides for e in s['events']]
assert flat==[e['id'] for e in events]
htmltext=(R/'index.html').read_text(encoding='utf8')
assert all(e['id'] in htmltext for e in events)
assert '待定：第二课' not in htmltext
audit={'slides':len(articles),'text_lines':sum(e['type']=='text' for e in events),'original_images':sum(e['type']=='figure' for e in events),'source_pages':14,'source_boundary':'第14页待定：第二课之前','all_events_in_order':True,'source_sha256':hashlib.sha256((R/'source-content.json').read_bytes()).hexdigest()}
(R/'coverage.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(audit,ensure_ascii=False))
