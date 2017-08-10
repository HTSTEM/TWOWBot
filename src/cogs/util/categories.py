def category(cat):
    def set_cat(cmd):
        cmd.category = cat.title()
        return cmd
    return set_cat