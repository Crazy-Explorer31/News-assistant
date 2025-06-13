#!/bin/bash

if [ -z "$1" ]; then
  echo "Использование: $0 <путь_к_директории> [--only-pycodestyle]"
  exit 1
fi

TARGET_DIR="$1"
status=0

for file in $(find "$TARGET_DIR" -type f -name "*.py");
do
  echo "🔃🔃🔃🔃🔃🔃🔃 Проверяем файл: $file 🔃🔃🔃🔃🔃🔃🔃"

  pycodestyle --max-line-length=200 "$file"
  if [ $? -ne 0 ]; then
    echo "Ошибки pycodestyle в файле $file есть 👺"
    status=1
  else
      echo "Ошибок pycodestyle в файле $file нет 😎"
  fi
  
  echo "✅✅✅✅✅✅✅ Проверили файл: $file ✅✅✅✅✅✅✅"
  echo ""
done

echo "Всё проверили!"

exit $status
