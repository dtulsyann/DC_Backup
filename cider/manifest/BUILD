# Manifest genrules.

package(default_visibility = ["//datacommons"])

filegroup(
    name = "base_textprotos",
    srcs = glob(["base/*.textproto"]),
)

filegroup(
    name = "nonbase_textprotos",
    srcs = glob([
        "bio/*.textproto",
        "generated/*.textproto",
        "india_stats/*.textproto",
        "international_stats/*.textproto",
        "ipcc/*.textproto",
        "us_census/*.textproto",
        "us_stats/*.textproto",
    ]),
)

genrule(
    name = "resolved_mcfs_merger",
    srcs = [
        "prod_dataset_info.textproto",
        ":base_textprotos",
        ":nonbase_textprotos",
        "prod_import_groups.textproto",
        "prod_import_mcf.textproto",
    ],
    outs = ["resolved_mcfs.textproto"],
    cmd = """
      cat \\
        $(location prod_dataset_info.textproto) \\
        $(locations :base_textprotos) \\
        $(locations :nonbase_textprotos) \\
        $(location prod_import_groups.textproto) \\
        $(location prod_import_mcf.textproto) \\
        > $@
    """,
)

genrule(
    name = "core_resolved_mcfs_merger",
    srcs = [
        "prod_dataset_info.textproto",
        ":base_textprotos",
        "prod_import_groups.textproto",
        "prod_import_mcf.textproto",
    ],
    outs = ["core_resolved_mcfs.textproto"],
    cmd = """
      cat \\
        $(location prod_dataset_info.textproto) \\
        $(location prod_import_groups.textproto) \\
        $(location prod_import_mcf.textproto) \\
        $(locations :base_textprotos) \\
        > $@
    """,
)
