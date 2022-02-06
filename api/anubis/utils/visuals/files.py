from io import BytesIO


def convert_fig_bytes(plt, fig) -> bytes:
    file_bytes = BytesIO()

    fig.tight_layout()
    fig.patch.set_facecolor("white")
    plt.savefig(file_bytes)

    file_bytes.seek(0)

    return file_bytes.read()