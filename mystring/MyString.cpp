#include "MyString.h"
#include <array>
#include <cstring>
#include <queue>
#include <stdexcept>
#include <vector>

namespace {
void validate_non_negative_count(int count) {
    if (count < 0) {
        throw std::invalid_argument("count must be non-negative");
    }
}
}

// Конструкторы и деструктор (1-9).
// Создаёт пустую строку.
MyString::MyString() : data_(new char[1]), size_(0), capacity_(0) {
    data_[0] = '\0';
}

// Копирует count символов из C-строки.
MyString::MyString(const char* str, int count) : MyString() {
    validate_count(source_length(str), count);
    Assign(str, count);
}

// Копирует count символов из std::string.
MyString::MyString(const std::string& str, int count) : MyString(str.c_str(), count) {}

// Копирует count символов из MyString.
MyString::MyString(const MyString& str, int count) : MyString(str.data_, count) {}

// Копирует всю C-строку.
MyString::MyString(const char* str) : MyString() {
    Assign(str, source_length(str));
}

// Копирует всю std::string.
MyString::MyString(const std::string& str) : MyString(str.c_str(), static_cast<int>(str.size())) {}

// Создаёт глубокую копию MyString.
MyString::MyString(const MyString& str) : MyString(str.data_, str.size_) {}

// Создаёт строку из count одинаковых символов.
MyString::MyString(int count, char ch) : MyString() {
    validate_non_negative_count(count);
    ensure_capacity(count + 1);
    std::memset(data_, static_cast<unsigned char>(ch), static_cast<std::size_t>(count));
    size_ = count;
    data_[size_] = '\0';
}

// Освобождает выделенную память.
MyString::~MyString() {
    delete[] data_;
}

// Очистка строки и уменьшение памяти (10-11).
// Очищает строку, сохраняя capacity.
void MyString::clear() {
    size_ = 0;
    data_[0] = '\0';
}

// Уменьшает capacity до минимального значения.
void MyString::shrink_to_fit() {
    const int target_capacity = size_ == 0 ? 0 : size_ + 1;
    if (capacity_ == target_capacity) {
        return;
    }

    char* new_data = new char[target_capacity == 0 ? 1 : target_capacity];
    if (size_ > 0) {
        std::memcpy(new_data, data_, static_cast<std::size_t>(size_));
    }
    new_data[size_] = '\0';
    delete[] data_;
    data_ = new_data;
    capacity_ = target_capacity;
}

// Операторы присваивания (12-13).
// Присваивает C-строку.
MyString& MyString::operator=(const char* str) {
    Assign(str, source_length(str));
    return *this;
}

// Присваивает std::string.
MyString& MyString::operator=(const std::string& str) {
    Assign(str.c_str(), static_cast<int>(str.size()));
    return *this;
}

// Присваивает другой MyString.
MyString& MyString::operator=(const MyString& str) {
    if (this != &str) {
        Assign(str.data_, str.size_);
    }
    return *this;
}

// Присваивает один символ.
MyString& MyString::operator=(char ch) {
    ensure_capacity(2);
    data_[0] = ch;
    data_[1] = '\0';
    size_ = 1;
    return *this;
}

// Методы получения свойств (14-17).
// Возвращает C-строку.
const char* MyString::c_str() const {
    return data_;
}

// Возвращает количество символов.
int MyString::size() const {
    return size_;
}

// Возвращает текущую ёмкость.
int MyString::capacity() const {
    return capacity_;
}

// Проверяет, пустая ли строка.
bool MyString::empty() const {
    return size_ == 0;
}

// Методы вставки (18-27).
// Вставляет count одинаковых символов по индексу.
MyString& MyString::insert(int index, int count, char ch) {
    validate_insert_index(index);
    MyString fragment(count, ch);
    return insert(index, fragment);
}

// Вставляет всю C-строку по индексу.
MyString& MyString::insert(int index, const char* str) {
    const int str_size = source_length(str);
    return insert_impl(index, str, str_size, 0, str_size);
}

// Вставляет всю std::string по индексу.
MyString& MyString::insert(int index, const std::string& str) {
    return insert_impl(index, str.c_str(), static_cast<int>(str.size()), 0, static_cast<int>(str.size()));
}

// Вставляет весь MyString по индексу.
MyString& MyString::insert(int index, const MyString& str) {
    return insert_impl(index, str.data_, str.size_, 0, str.size_);
}

// Вставляет первые count символов C-строки.
MyString& MyString::insert(int index, const char* str, int count) {
    return insert_impl(index, str, source_length(str), 0, count);
}

// Вставляет первые count символов std::string.
MyString& MyString::insert(int index, const std::string& str, int count) {
    return insert_impl(index, str.c_str(), static_cast<int>(str.size()), 0, count);
}

// Вставляет первые count символов MyString.
MyString& MyString::insert(int index, const MyString& str, int count) {
    return insert_impl(index, str.data_, str.size_, 0, count);
}

// Вставляет часть C-строки по индексу.
MyString& MyString::insert(int index, const char* str, int source_index, int count) {
    return insert_impl(index, str, source_length(str), source_index, count);
}

// Вставляет часть std::string по индексу.
MyString& MyString::insert(int index, const std::string& str, int source_index, int count) {
    return insert_impl(index, str.c_str(), static_cast<int>(str.size()), source_index, count);
}

// Вставляет часть MyString по индексу.
MyString& MyString::insert(int index, const MyString& str, int source_index, int count) {
    return insert_impl(index, str.data_, str.size_, source_index, count);
}

// Методы добавления в конец (28-37).
// Добавляет count одинаковых символов.
MyString& MyString::append(int count, char ch) {
    return insert(size_, count, ch);
}

// Добавляет всю C-строку.
MyString& MyString::append(const char* str) {
    return insert(size_, str);
}

// Добавляет всю std::string.
MyString& MyString::append(const std::string& str) {
    return insert(size_, str);
}

// Добавляет весь MyString.
MyString& MyString::append(const MyString& str) {
    return insert(size_, str);
}

// Добавляет первые count символов C-строки.
MyString& MyString::append(const char* str, int count) {
    return insert(size_, str, count);
}

// Добавляет первые count символов std::string.
MyString& MyString::append(const std::string& str, int count) {
    return insert(size_, str, count);
}

// Добавляет первые count символов MyString.
MyString& MyString::append(const MyString& str, int count) {
    return insert(size_, str, count);
}

// Добавляет часть C-строки.
MyString& MyString::append(const char* str, int source_index, int count) {
    return insert(size_, str, source_index, count);
}

// Добавляет часть std::string.
MyString& MyString::append(const std::string& str, int source_index, int count) {
    return insert(size_, str, source_index, count);
}

// Добавляет часть MyString.
MyString& MyString::append(const MyString& str, int source_index, int count) {
    return insert(size_, str, source_index, count);
}

// Метод удаления.
// Удаляет count символов по индексу.
MyString& MyString::erase(int index, int count) {
    if (index < 0 || index > size_) {
        throw std::out_of_range("index is outside the string");
    }
    if (count < 0 || count > size_ - index) {
        throw std::out_of_range("erase range is outside the string");
    }

    std::memmove(data_ + index, data_ + index + count,
                 static_cast<std::size_t>(size_ - index - count + 1));
    size_ -= count;
    return *this;
}

// Методы замены подстроки.
// Заменяет часть строки всей C-строкой.
MyString& MyString::replace(int index, int count, const char* str) {
    const int str_size = source_length(str);
    return replace_impl(index, count, str, str_size, 0, str_size);
}

// Заменяет часть строки всей std::string.
MyString& MyString::replace(int index, int count, const std::string& str) {
    return replace_impl(index, count, str.c_str(), static_cast<int>(str.size()), 0,
                        static_cast<int>(str.size()));
}

// Заменяет часть строки всем MyString.
MyString& MyString::replace(int index, int count, const MyString& str) {
    return replace_impl(index, count, str.data_, str.size_, 0, str.size_);
}

// Заменяет часть строки началом C-строки.
MyString& MyString::replace(int index, int count, const char* str, int source_count) {
    return replace_impl(index, count, str, source_length(str), 0, source_count);
}

// Заменяет часть строки началом std::string.
MyString& MyString::replace(int index, int count, const std::string& str, int source_count) {
    return replace_impl(index, count, str.c_str(), static_cast<int>(str.size()), 0, source_count);
}

// Заменяет часть строки началом MyString.
MyString& MyString::replace(int index, int count, const MyString& str, int source_count) {
    return replace_impl(index, count, str.data_, str.size_, 0, source_count);
}

// Заменяет часть строки срезом C-строки.
MyString& MyString::replace(int index, int count, const char* str, int source_index, int source_count) {
    return replace_impl(index, count, str, source_length(str), source_index, source_count);
}

// Заменяет часть строки срезом std::string.
MyString& MyString::replace(int index, int count, const std::string& str, int source_index,
                             int source_count) {
    return replace_impl(index, count, str.c_str(), static_cast<int>(str.size()), source_index, source_count);
}

// Заменяет часть строки срезом MyString.
MyString& MyString::replace(int index, int count, const MyString& str, int source_index, int source_count) {
    return replace_impl(index, count, str.data_, str.size_, source_index, source_count);
}

// Методы получения подстроки (48-49).
// Возвращает подстроку от index до конца.
MyString MyString::substr(int index) const {
    if (index < 0 || index > size_) {
        throw std::out_of_range("index is outside the string");
    }
    return MyString(data_ + index, size_ - index);
}

// Возвращает count символов начиная с index.
MyString MyString::substr(int index, int count) const {
    validate_slice(size_, index, count);
    return MyString(data_ + index, count);
}

// Операторы объединения строк (50-55).
// Объединяет текущую строку с C-строкой.
MyString MyString::operator+(const char* str) const {
    MyString result(*this);
    result.append(str);
    return result;
}

// Объединяет текущую строку со std::string.
MyString MyString::operator+(const std::string& str) const {
    MyString result(*this);
    result.append(str);
    return result;
}

// Объединяет текущую строку с MyString.
MyString MyString::operator+(const MyString& str) const {
    MyString result(*this);
    result.append(str);
    return result;
}

// Добавляет C-строку к текущей строке.
MyString& MyString::operator+=(const char* str) {
    return append(str);
}

// Добавляет std::string к текущей строке.
MyString& MyString::operator+=(const std::string& str) {
    return append(str);
}

// Добавляет MyString к текущей строке.
MyString& MyString::operator+=(const MyString& str) {
    return append(str);
}

// Оператор индексации (56).
// Возвращает изменяемый символ по индексу.
char& MyString::operator[](int index) {
    validate_index(index);
    return data_[index];
}

// Возвращает символ константной строки.
const char& MyString::operator[](int index) const {
    validate_index(index);
    return data_[index];
}

// Сравнение строк (57-60).
// Лексикографически сравнивает две строки.
int MyString::compare(const MyString& str) const {
    const int common_size = size_ < str.size_ ? size_ : str.size_;
    for (int i = 0; i < common_size; ++i) {
        if (data_[i] < str.data_[i]) {
            return -1;
        }
        if (data_[i] > str.data_[i]) {
            return 1;
        }
    }

    if (size_ < str.size_) {
        return -1;
    }
    if (size_ > str.size_) {
        return 1;
    }
    return 0;
}

// Проверяет, больше ли текущая строка.
bool MyString::operator>(const MyString& str) const {
    return compare(str) > 0;
}

// Проверяет, меньше ли текущая строка.
bool MyString::operator<(const MyString& str) const {
    return compare(str) < 0;
}

// Проверяет условие «больше или равно».
bool MyString::operator>=(const MyString& str) const {
    return compare(str) >= 0;
}

// Проверяет условие «меньше или равно».
bool MyString::operator<=(const MyString& str) const {
    return compare(str) <= 0;
}

// Проверяет строки на неравенство.
bool MyString::operator!=(const MyString& str) const {
    return compare(str) != 0;
}

// Проверяет строки на равенство.
bool MyString::operator==(const MyString& str) const {
    return compare(str) == 0;
}

// Методы поиска подстроки (61-66).
// Ищет C-строку с начала.
int MyString::find(const char* str) const {
    return find(str, 0);
}

// Ищет std::string с начала.
int MyString::find(const std::string& str) const {
    return find(str, 0);
}

// Ищет MyString с начала.
int MyString::find(const MyString& str) const {
    return find(str, 0);
}

// Ищет C-строку начиная с index.
int MyString::find(const char* str, int index) const {
    return find_impl(str, source_length(str), index);
}

// Ищет std::string начиная с index.
int MyString::find(const std::string& str, int index) const {
    return find_impl(str.c_str(), static_cast<int>(str.size()), index);
}

// Ищет MyString начиная с index.
int MyString::find(const MyString& str, int index) const {
    return find_impl(str.data_, str.size_, index);
}

// Выполняет поиск подстроки по алгоритму Ахо-Корасика.
int MyString::find_impl(const char* str, int str_size, int index) const {
    std::vector<MyString> patterns;
    patterns.emplace_back(str, str_size);
    return find_all_impl(patterns, index)[0];
}

// Строит автомат для шаблонов и ищет их от start_index одним проходом текста.
std::vector<int> MyString::find_all_impl(const std::vector<MyString>& patterns,
                                         int start_index) const {
    struct Node {
        std::array<int, 256> next;
        int suffix_link;
        std::vector<int> pattern_indexes;

        Node() : suffix_link(0) {
            next.fill(-1);
        }
    };

    if (start_index < 0 || start_index > size_) {
        throw std::out_of_range("index is outside the string");
    }

    std::vector<int> positions(patterns.size(), -1);
    std::vector<Node> nodes(1);

    // Строим бор сразу для всех непустых шаблонов.
    for (std::size_t pattern_index = 0; pattern_index < patterns.size(); ++pattern_index) {
        if (patterns[pattern_index].size_ == 0) {
            positions[pattern_index] = start_index;
            continue;
        }

        int state = 0;
        for (int symbol_index = 0; symbol_index < patterns[pattern_index].size_; ++symbol_index) {
            const unsigned char symbol =
                static_cast<unsigned char>(patterns[pattern_index].data_[symbol_index]);
            if (nodes[state].next[symbol] == -1) {
                nodes[state].next[symbol] = static_cast<int>(nodes.size());
                nodes.emplace_back();
            }
            state = nodes[state].next[symbol];
        }
        nodes[state].pattern_indexes.push_back(static_cast<int>(pattern_index));
    }

    // Строим суффиксные ссылки и полные переходы автомата.
    std::queue<int> states;
    for (int symbol = 0; symbol < 256; ++symbol) {
        const int next_state = nodes[0].next[symbol];
        if (next_state == -1) {
            nodes[0].next[symbol] = 0;
        } else {
            states.push(next_state);
        }
    }

    while (!states.empty()) {
        const int current = states.front();
        states.pop();

        for (int symbol = 0; symbol < 256; ++symbol) {
            const int next_state = nodes[current].next[symbol];
            if (next_state == -1) {
                nodes[current].next[symbol] = nodes[nodes[current].suffix_link].next[symbol];
            } else {
                const int suffix_state = nodes[nodes[current].suffix_link].next[symbol];
                nodes[next_state].suffix_link = suffix_state;
                nodes[next_state].pattern_indexes.insert(
                    nodes[next_state].pattern_indexes.end(),
                    nodes[suffix_state].pattern_indexes.begin(),
                    nodes[suffix_state].pattern_indexes.end());
                states.push(next_state);
            }
        }
    }

    // Проходим текст один раз и запоминаем первое вхождение каждого шаблона.
    int state = 0;
    for (int text_index = start_index; text_index < size_; ++text_index) {
        const unsigned char symbol = static_cast<unsigned char>(data_[text_index]);
        state = nodes[state].next[symbol];

        for (int pattern_index : nodes[state].pattern_indexes) {
            if (positions[pattern_index] == -1) {
                positions[pattern_index] = text_index - patterns[pattern_index].size_ + 1;
            }
        }
    }

    return positions;
}

// Ищет первые вхождения всех шаблонов от начала строки.
std::vector<int> MyString::find_all(const std::vector<MyString>& patterns) const {
    return find_all_impl(patterns, 0);
}

// Метод из приложения к заданию.
// Возвращает длину строки.
int MyString::length() const {
    return size();
}

// Вспомогательные методы основной таблицы.
// Проверяет указатель и возвращает длину C-строки.
int MyString::source_length(const char* str) {
    if (str == nullptr) {
        throw std::invalid_argument("source string must not be null");
    }
    return static_cast<int>(std::strlen(str));
}

// Проверяет допустимое количество символов.
void MyString::validate_count(int source_size, int count) {
    if (count < 0 || count > source_size) {
        throw std::out_of_range("count is outside the source string");
    }
}

// Проверяет границы среза исходной строки.
void MyString::validate_slice(int source_size, int source_index, int count) {
    if (source_index < 0 || count < 0 || source_index > source_size || source_index + count > source_size) {
        throw std::out_of_range("source range is outside the string");
    }
}

// Проверяет индекс существующего символа.
void MyString::validate_index(int index) const {
    if (index < 0 || index >= size_) {
        throw std::out_of_range("index is outside the string");
    }
}

// Проверяет индекс для вставки.
void MyString::validate_insert_index(int index) const {
    if (index < 0 || index > size_) {
        throw std::out_of_range("index is outside the string");
    }
}

// Увеличивает буфер при нехватке памяти.
void MyString::ensure_capacity(int required_capacity) {
    if (required_capacity <= capacity_) {
        return;
    }

    char* new_data = new char[required_capacity];
    if (size_ > 0) {
        std::memcpy(new_data, data_, static_cast<std::size_t>(size_));
    }
    new_data[size_] = '\0';
    delete[] data_;
    data_ = new_data;
    capacity_ = required_capacity;
}

// Копирует символы и обновляет размер строки.
void MyString::Assign(const char* str, int count) {
    ensure_capacity(count + 1);
    std::memmove(data_, str, static_cast<std::size_t>(count));
    size_ = count;
    data_[size_] = '\0';
}

// Выполняет общую вставку строкового фрагмента.
MyString& MyString::insert_impl(int index, const char* str, int source_size, int source_index, int count) {
    validate_insert_index(index);
    validate_slice(source_size, source_index, count);
    if (count == 0) {
        return *this;
    }

    // Копия нужна, если источник находится в data_ этой же строки.
    char* fragment = new char[count];
    std::memcpy(fragment, str + source_index, static_cast<std::size_t>(count));

    try {
        ensure_capacity(size_ + count + 1);
    } catch (...) {
        delete[] fragment;
        throw;
    }

    std::memmove(data_ + index + count, data_ + index,
                 static_cast<std::size_t>(size_ - index + 1));
    std::memcpy(data_ + index, fragment, static_cast<std::size_t>(count));
    delete[] fragment;
    size_ += count;
    return *this;
}

// Выполняет общую замену строкового фрагмента.
MyString& MyString::replace_impl(int index, int count, const char* str, int source_size,
                                  int source_index, int source_count) {
    if (index < 0 || index > size_) {
        throw std::out_of_range("index is outside the string");
    }
    if (count < 0 || count > size_ - index) {
        throw std::out_of_range("replace range is outside the string");
    }
    validate_slice(source_size, source_index, source_count);

    if (source_count == 0) {
        return erase(index, count);
    }
    MyString fragment(str + source_index, source_count);
    insert(index, fragment);
    return erase(index + source_count, count);
}

// 6.2 итератор.
MyString& MyString::insert(iterator position, int count, char ch) {
    return insert(iterator_index(position), count, ch);
}

MyString& MyString::insert(iterator position, const char* str) {
    return insert(iterator_index(position), str);
}

MyString& MyString::insert(iterator position, const std::string& str) {
    return insert(iterator_index(position), str);
}

MyString& MyString::insert(iterator position, const MyString& str) {
    return insert(iterator_index(position), str);
}

MyString& MyString::insert(iterator position, const char* str, int count) {
    return insert(iterator_index(position), str, count);
}

MyString& MyString::insert(iterator position, const std::string& str, int count) {
    return insert(iterator_index(position), str, count);
}

MyString& MyString::insert(iterator position, const MyString& str, int count) {
    return insert(iterator_index(position), str, count);
}

MyString& MyString::insert(iterator position, const char* str, int source_index, int count) {
    return insert(iterator_index(position), str, source_index, count);
}

MyString& MyString::insert(iterator position, const std::string& str,
                           int source_index, int count) {
    return insert(iterator_index(position), str, source_index, count);
}

MyString& MyString::insert(iterator position, const MyString& str,
                           int source_index, int count) {
    return insert(iterator_index(position), str, source_index, count);
}

MyString& MyString::erase(iterator position, int count) {
    return erase(iterator_index(position), count);
}

MyString& MyString::replace(iterator position, int count, const char* str) {
    return replace(iterator_index(position), count, str);
}

MyString& MyString::replace(iterator position, int count, const std::string& str) {
    return replace(iterator_index(position), count, str);
}

MyString& MyString::replace(iterator position, int count, const MyString& str) {
    return replace(iterator_index(position), count, str);
}

MyString& MyString::replace(iterator position, int count, const char* str, int source_count) {
    return replace(iterator_index(position), count, str, source_count);
}

MyString& MyString::replace(iterator position, int count, const std::string& str,
                            int source_count) {
    return replace(iterator_index(position), count, str, source_count);
}

MyString& MyString::replace(iterator position, int count, const MyString& str,
                            int source_count) {
    return replace(iterator_index(position), count, str, source_count);
}

MyString& MyString::replace(iterator position, int count, const char* str,
                            int source_index, int source_count) {
    return replace(iterator_index(position), count, str, source_index, source_count);
}

MyString& MyString::replace(iterator position, int count, const std::string& str,
                            int source_index, int source_count) {
    return replace(iterator_index(position), count, str, source_index, source_count);
}

MyString& MyString::replace(iterator position, int count, const MyString& str,
                            int source_index, int source_count) {
    return replace(iterator_index(position), count, str, source_index, source_count);
}

MyString MyString::substr(const_iterator position) const {
    return substr(iterator_index(position));
}

MyString MyString::substr(const_iterator position, int count) const {
    return substr(iterator_index(position), count);
}

int MyString::find(const char* str, const_iterator position) const {
    return find(str, iterator_index(position));
}

int MyString::find(const std::string& str, const_iterator position) const {
    return find(str, iterator_index(position));
}

int MyString::find(const MyString& str, const_iterator position) const {
    return find(str, iterator_index(position));
}

char& MyString::operator[](iterator position) {
    return operator[](iterator_index(position));
}

const char& MyString::operator[](const_iterator position) const {
    return operator[](iterator_index(position));
}

char& MyString::at(iterator position) {
    return at(iterator_index(position));
}

const char& MyString::at(const_iterator position) const {
    return at(iterator_index(position));
}
