import glob, os, argparse
from board import BLACK, WHITE, EMPTY, INVLD

class SgfParser:
    def __init__(self, sgf_string):
        self.history = list()
        self.black_player = str()
        self.white_player = str()
        self.winner = INVLD
        self.board_size = None
        self.komi = None
        self._parse(sgf_string)

    def _process_key_value(self, key, val):
        def as_move(m, bsize=self.board_size):
            if len(m) == 0 or m == "tt":
                return None
            x = ord(m[0]) - ord('a')
            y = ord(m[1]) - ord('a')
            y = bsize - 1 - y
            return (x, y)

        if key == "SZ":
            self.board_size = int(val)
        elif key == "KM":
            self.komi = float(val)
        elif key == "B":
            self.history.append((BLACK, as_move(val)))
        elif key == "W":
            self.history.append((WHITE, as_move(val)))
        elif key == "PB":
            self.black_player = val
        elif key == "PW":
            self.white_player = val
        elif key == "AB" or key == "AW":
            raise Exception("Do not support for AB/AW tag in the SGF file.")
        elif key == "RE":
            if "B+" in val:
                self.winner = BLACK
            elif "W+" in val:
                self.winner = WHITE
            elif val == "0":
                self.winner = EMPTY
            else:
                self.winner = INVLD

    def _parse(self, sgf):
        nesting = 0
        idx = 0
        node_cnt = 0
        key = str()
        while idx < len(sgf):
            c = sgf[idx]
            idx += 1;

            if c == '(':
                nesting += 1
            elif c == ')':
                nesting -= 1

            if c in ['(', ')', '\t', '\n', '\r'] or nesting != 1:
                continue
            elif c == ';':
                node_cnt += 1
            elif c == '[':
                end = sgf.find(']', idx)
                val = sgf[idx:end]
                self._process_key_value(key, val)
                key = str()
                idx = end+1
            else:
                key += c

def _load_file(filename):
    try:
        with open(filename, "r") as f:
            data = f.read().strip()
    except Exception as e:
        print(e)
        return None
    return data

def chop_sgfs_string(sgfs_string):
    sgfs_list = list()
    sgfs_string = sgfs_string.strip()

    nesting = 0
    head_idx = 0
    tail_idx = 0
    while tail_idx < len(sgfs_string):
        c = sgfs_string[tail_idx]
        tail_idx += 1;

        if c == '(':
            if nesting == 0:
                head_idx = tail_idx - 1
            nesting += 1
        elif c == ')':
            nesting -= 1
            if nesting == 0:
                sgfs_list.append(sgfs_string[head_idx:tail_idx])

        if c in ['(', ')', ';', '\t', '\n', '\r'] or nesting != 1:
            continue
        elif c == '[':
            end = sgfs_string.find(']', tail_idx)
            tail_idx = end + 1
    return sgfs_list

def parse_from_dir(root):
    sgfs_files = list()
    sgfs_files.extend(glob.glob(os.path.join(root, "*.sgf")))
    sgfs_files.extend(glob.glob(os.path.join(root, "*.sgfs")))
    sgfs = list()
    for filename in sgfs_files:
        data = _load_file(filename)
        if data:
            sgfs_list = chop_sgfs_string(data)
            for sgf_string in sgfs_list:
                try:
                    sgf = SgfParser(sgf_string)
                    sgfs.append(sgf)
                except Exception as e:
                    print(e)
    return sgfs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--sgf-dir", metavar="<string>",
                        help="input SGF directory", type=str)
    args = parser.parse_args()

    try:
        sgfs = parse_from_dir(args.sgf_dir)
        print("\nSuccessfuly parse every SGF string...")
    except Exception as e:
        print(e)
