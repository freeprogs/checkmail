
# checkmail

Checks mail for incoming messages.

If some mail has come it prints number of messages in the box and some
message headers like sender address and subject.

---

### Requirements

This program has tested in Linux Fedora 20 with Python 3.x installed.

### Building

Build the docs and read the README file in _build/docs_.

To build run:

```sh
$ ./configure
$ make
```

### Testing

To run unit-tests run:

```sh
$ make test
```

### Installation

To install run:

```sh
$ sudo make install
```

To uninstall run:

```sh
$ sudo make uninstall
```

---

Note:
Don't take files from this project before their building because they
are just templates for the ending program and its documentation. These
files may not work because template strings may brake the code as they
may be placed in the middle of code, not only in comments.
