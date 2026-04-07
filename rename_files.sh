#!/bin/bash
# 批量重命名 HTML 文件，格式：文件ID_原文件名.html

ARTICLE_IDS_DIR="userdata/article_ids"
USERFILES_DIR="userdata/userfiles"

echo "开始批量重命名文件..."
count=0

for id_file in "$ARTICLE_IDS_DIR"/*.txt; do
    # 获取文件 ID（去掉 .txt 后缀）
    file_id=$(basename "$id_file" .txt)
    
    # 读取文件内容，获取原路径
    old_path=$(cat "$id_file" | tr -d '\n')
    
    # 提取原文件名
    old_filename=$(basename "$old_path")
    
    # 构建新文件名：文件ID_原文件名
    new_filename="${file_id}_${old_filename}"
    
    # 构建完整路径
    old_fullpath="$USERFILES_DIR/$old_filename"
    new_fullpath="$USERFILES_DIR/$new_filename"
    
    # 检查原文件是否存在
    if [ -f "$old_fullpath" ]; then
        # 重命名文件
        mv "$old_fullpath" "$new_fullpath"
        
        # 更新 article_ids 文件中的路径
        echo "userdata/userfiles/$new_filename" > "$id_file"
        
        echo "✓ $old_filename -> $new_filename"
        count=$((count + 1))
    else
        echo "✗ 文件不存在: $old_fullpath"
    fi
done

echo ""
echo "完成！共重命名 $count 个文件"
