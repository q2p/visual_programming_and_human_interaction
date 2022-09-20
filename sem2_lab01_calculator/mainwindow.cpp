#include "mainwindow.h"

#include <QVBoxLayout>
#include <QLineEdit>
#include <QLineEdit>
#include <QToolButton>
#include <QSize>

Widget::Widget(QWidget *parent) : QWidget(parent) {
    auto vbox = new QVBoxLayout(this);
    auto edit_line = new QLineEdit();
    auto grid = new QGridLayout();

    edit_line->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
    edit_line->setReadOnly(true);
    edit_line->setMaxLength(32);

    std::array<QString, 6> colors = {
        "background-color: #aaf",
        "background-color: #afa",
        "background-color: #faa",
        "background-color: #aff",
        "background-color: #faf",
        "background-color: #ffa",
    };

    std::array<QString, 30> values = {
        "CR", "C", "(", ")", "Sin",
         "1", "2", "3", "+", "Cos",
         "4", "5", "6", "-", "Tg",
         "7", "8", "9", "*", "Ctg",
         ".", "0", "=", "/", "Sqrt",
         "!", "^", "Log2", "Log10", "Ln"
    };

    std::array<int, 30> funcs = {
        1, 1, 5, 5, 2,
        0, 0, 0, 5, 2,
        0, 0, 0, 5, 2,
        0, 0, 0, 5, 2,
        5, 0, 5, 5, 4,
        4, 4, 3, 3, 3,
    };

    for (size_t i = 0; i < values.size(); i++){
        auto x = i % 5;
        auto y = i / 5;
        auto b = new QToolButton();
        b->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        b->setText(values[i]);
        b->setMinimumSize(40, 40);
        b->setStyleSheet(colors[funcs[i]]);
        grid->addWidget(b, y, x);
    }

    vbox->addWidget(edit_line);
    vbox->addLayout(grid);
    setLayout(vbox);
}
