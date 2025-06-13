#!/bin/bash

if [ -z "$1" ]; then
  echo "Использование: $0 <путь_к_директории>"
  exit 1
fi

TARGET_DIR="$1"

find "$TARGET_DIR" -type f -name "*.py" | while read -r file; do
  echo "Форматируем файл: $file"
  
  autoflake --remove-all-unused-imports --in-place "$file"
  
  isort "$file"
  
  black "$file"
  
  echo "Отформатировали файл: $file"
done

echo "Всё отформатировали!"
