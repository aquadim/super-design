python3 ui-compiler.py
glib-compile-resources resources.xml --target=resources.gresource
gtk-builder-tool validate ui/properties/*.compiled.ui
