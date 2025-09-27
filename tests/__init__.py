import gettext

lang = gettext.translation('messages', localedir='shoestring_ce/lang', languages=('ja',))
lang.install()
