import re

with open('gen_report.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    stripped = line.strip()
    # 匹配 body("...")  其中 ... 可能包含内嵌的 ASCII 双引号
    if stripped.startswith(('body("', "body('")) and stripped.endswith(('"),', "'),", '"),', "'),")):
        # 把 body("..."), 或 body('...'), 转为 body(`...`),
        content = stripped[5:-2]  # 去掉 body( 和 ),
        # 用反引号包裹
        new_line = line[:len(line) - len(stripped)] + 'body(`' + content + '`),\n'
        fixed_lines.append(new_line)
    elif stripped.startswith(('bodyNoIndent("', "bodyNoIndent('")):
        content = stripped[13:-2]
        new_line = line[:len(line) - len(stripped)] + 'bodyNoIndent(`' + content + '`),\n'
        fixed_lines.append(new_line)
    else:
        fixed_lines.append(line)

with open('gen_report.js', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print('Converted body() calls to template literals')
