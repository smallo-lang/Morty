# Morty

Morty is a snappy and lightweight assembler for the SmallO assembly.



## Architecture

### <a name="loader"></a> Loader

The loader is supposed to 

1. Read input file and process includes;
2. Clean the code of redundant data (e.g. empty lines, comments, whitespace);
3. Pass it onto the [preprocessor](preprocessor).


### <a name="preprocessor"></a> Preprocessor

The preprocessor is supposed to

1. Receive code from the [loader](loader);
2. Compose names table made of labels and variables and make sure there are no
   label duplicates;
3. Record constant literals and outline memory space based on the names table;
4. Compile the instructions list by parsing SmallO assembly.
5. Produce bytecode for [Rick](https://github.com/smallo-lang/Rick).



## License

This project is licensed under the **Mozilla Public License Version 2.0** --
see the [LICENSE](LICENSE) file for details.

Please note that this project is distributred as is,
**with absolutely no warranty of any kind** to those who are going to deploy
and/or use it. None of the authors and contributors are responsible (liable)
for **any damage**, including but not limited to, loss of sensitive data and
machine malfunction.
