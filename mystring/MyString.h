#ifndef _MYSTRING_H_
#define _MYSTRING_H_

#include "MyStringIterator.h"

#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

class MyString {
public:
    // Constructors and destructor (1-9).
    MyString();
    MyString(const char* str);
    MyString(const std::string& str);
    MyString(const MyString& str);
    MyString(const char* str, int count);
    MyString(const std::string& str, int count);
    MyString(const MyString& str, int count);
    MyString(int count, char ch);
    ~MyString();

    // Clear and memory reduction (10-11).
    void clear();
    void shrink_to_fit();

    // Assignment operators (12-13).
    MyString& operator=(const char* str);
    MyString& operator=(const std::string& str);
    MyString& operator=(const MyString& str);
    MyString& operator=(char ch);

    // Getters (14-17).
    const char* c_str() const;
    int size() const;
    int capacity() const;
    bool empty() const;

    // Insert methods (18-27).
    MyString& insert(int index, int count, char ch);
    MyString& insert(int index, const char* str);
    MyString& insert(int index, const std::string& str);
    MyString& insert(int index, const MyString& str);
    MyString& insert(int index, const char* str, int count);
    MyString& insert(int index, const std::string& str, int count);
    MyString& insert(int index, const MyString& str, int count);
    MyString& insert(int index, const char* str, int source_index, int count);
    MyString& insert(int index, const std::string& str, int source_index, int count);
    MyString& insert(int index, const MyString& str, int source_index, int count);

    // Append methods (28-37).
    MyString& append(int count, char ch);
    MyString& append(const char* str);
    MyString& append(const std::string& str);
    MyString& append(const MyString& str);
    MyString& append(const char* str, int count);
    MyString& append(const std::string& str, int count);
    MyString& append(const MyString& str, int count);
    MyString& append(const char* str, int source_index, int count);
    MyString& append(const std::string& str, int source_index, int count);
    MyString& append(const MyString& str, int source_index, int count);

    // Erase method.
    MyString& erase(int index, int count);

    // Replace methods.
    MyString& replace(int index, int count, const char* str);
    MyString& replace(int index, int count, const std::string& str);
    MyString& replace(int index, int count, const MyString& str);
    MyString& replace(int index, int count, const char* str, int source_count);
    MyString& replace(int index, int count, const std::string& str, int source_count);
    MyString& replace(int index, int count, const MyString& str, int source_count);
    MyString& replace(int index, int count, const char* str, int source_index, int source_count);
    MyString& replace(int index, int count, const std::string& str, int source_index, int source_count);
    MyString& replace(int index, int count, const MyString& str, int source_index, int source_count);

    // Substring methods.
    MyString substr(int index) const;
    MyString substr(int index, int count) const;

    // Concatenation operators.
    MyString operator+(const char* str) const;
    MyString operator+(const std::string& str) const;
    MyString operator+(const MyString& str) const;
    MyString& operator+=(const char* str);
    MyString& operator+=(const std::string& str);
    MyString& operator+=(const MyString& str);

    // Index operator.
    char& operator[](int index);
    const char& operator[](int index) const;

    // String comparison.
    int compare(const MyString& str) const;
    bool operator>(const MyString& str) const;
    bool operator<(const MyString& str) const;
    bool operator>=(const MyString& str) const;
    bool operator<=(const MyString& str) const;
    bool operator!=(const MyString& str) const;
    bool operator==(const MyString& str) const;

    // Search methods.
    int find(const char* str) const;
    int find(const std::string& str) const;
    int find(const MyString& str) const;
    int find(const char* str, int index) const;
    int find(const std::string& str, int index) const;
    int find(const MyString& str, int index) const;

    // Ищет первые вхождения нескольких подстрок одним автоматом Ахо-Корасика.
    // Результаты идут в том же порядке, что и шаблоны; -1 означает «не найдено».
    std::vector<int> find_all(const std::vector<MyString>& patterns) const;

    // Метод из приложения к заданию.
    int length() const;

    // Дополнительное задание 6.1.
    // Забирает данные временного объекта без копирования.
    MyString(MyString&& str);

    // Преобразует целое число в MyString.
    MyString(int value);

    // Преобразует float в MyString.
    MyString(float value);

    // Забирает данные другого временного объекта.
    MyString& operator=(MyString&& str);

    // Преобразует MyString в целое число.
    int to_int() const;

    // Преобразует MyString в число типа float.
    float to_float() const;

    // Возвращает изменяемый символ или генерирует исключение.
    char& at(int index);

    // Возвращает символ константной строки или генерирует исключение.
    const char& at(int index) const;

    // Дополнительное задание 6.2.
    using iterator = MyStringIterator;
    using const_iterator = MyStringConstIterator;
    using reverse_iterator = MyStringReverseIterator;
    using const_reverse_iterator = MyStringConstReverseIterator;

    iterator begin();
    iterator end();
    const_iterator cbegin() const;
    const_iterator cend() const;
    reverse_iterator rbegin();
    reverse_iterator rend();
    const_reverse_iterator rcbegin() const;
    const_reverse_iterator rcend() const;

    // Вставляет данные по позиции итератора.
    MyString& insert(iterator position, int count, char ch);
    MyString& insert(iterator position, const char* str);
    MyString& insert(iterator position, const std::string& str);
    MyString& insert(iterator position, const MyString& str);
    MyString& insert(iterator position, const char* str, int count);
    MyString& insert(iterator position, const std::string& str, int count);
    MyString& insert(iterator position, const MyString& str, int count);
    MyString& insert(iterator position, const char* str, int source_index, int count);
    MyString& insert(iterator position, const std::string& str, int source_index, int count);
    MyString& insert(iterator position, const MyString& str, int source_index, int count);

    // Удаляет символы по позиции итератора.
    MyString& erase(iterator position, int count);

    // Заменяет символы по позиции итератора.
    MyString& replace(iterator position, int count, const char* str);
    MyString& replace(iterator position, int count, const std::string& str);
    MyString& replace(iterator position, int count, const MyString& str);
    MyString& replace(iterator position, int count, const char* str, int source_count);
    MyString& replace(iterator position, int count, const std::string& str, int source_count);
    MyString& replace(iterator position, int count, const MyString& str, int source_count);
    MyString& replace(iterator position, int count, const char* str,
                      int source_index, int source_count);
    MyString& replace(iterator position, int count, const std::string& str,
                      int source_index, int source_count);
    MyString& replace(iterator position, int count, const MyString& str,
                      int source_index, int source_count);

    // Создаёт подстроку от позиции итератора.
    MyString substr(const_iterator position) const;
    MyString substr(const_iterator position, int count) const;

    // Ищет подстроку от позиции итератора.
    int find(const char* str, const_iterator position) const;
    int find(const std::string& str, const_iterator position) const;
    int find(const MyString& str, const_iterator position) const;

    // Возвращает символ по позиции итератора с проверкой границ.
    char& at(iterator position);
    const char& at(const_iterator position) const;

    // Возвращает символ по позиции итератора.
    char& operator[](iterator position);
    const char& operator[](const_iterator position) const;

private:
    // Вспомогательные методы основной таблицы.
    // Получает длину C-строки.
    static int source_length(const char* str);

    // Проверяет количество символов.
    static void validate_count(int source_size, int count);

    // Проверяет границы среза.
    static void validate_slice(int source_size, int source_index, int count);

    // Проверяет индекс символа.
    void validate_index(int index) const;

    // Проверяет индекс вставки.
    void validate_insert_index(int index) const;

    // Увеличивает ёмкость буфера.
    void ensure_capacity(int required_capacity);

    // Записывает символы в текущую строку.
    void Assign(const char* str, int count);

    // Общая реализация вставки.
    MyString& insert_impl(int index, const char* str, int source_size, int source_index, int count);

    // Общая реализация замены.
    MyString& replace_impl(int index, int count, const char* str, int source_size,
                           int source_index, int source_count);

    // Преобразует итератор в индекс.
    int iterator_index(const_iterator position) const;

    char* data_;
    int size_;
    int capacity_;

    // Вспомогательные методы задания 6.1.
    // Ищет подстроку по алгоритму Ахо-Корасика.
    int find_impl(const char* str, int str_size, int index) const;

    // Строит один автомат Ахо-Корасика для всех шаблонов.
    std::vector<int> find_all_impl(const std::vector<MyString>& patterns,
                                   int start_index) const;

    // Удаляет лишние нули после точки.
    static std::string float_to_string(float value);

    // Читает знак числа.
    int parse_sign(int& index) const;
};

// Операторы дополнительного задания 6.1.
// Записывает MyString в файл.
std::ofstream& operator<<(std::ofstream& output, const MyString& str);

// Читает MyString из файла.
std::ifstream& operator>>(std::ifstream& input, MyString& str);

// Исключение при неверном преобразовании в число.
class InvalidConversion : public std::invalid_argument {
public:
    InvalidConversion() : std::invalid_argument("Invalid number format") {}
};

#endif  // _MYSTRING_H_
