#!/usr/bin/python3
import argparse
import os
import shutil
import hashlib
import datetime
import time


def process_agruments():
    parser = argparse.ArgumentParser(description='----------lgit.')
    parser.add_argument('command', nargs='+', help='-- add/commit/log...')
    parser.add_argument('-m', '--message', action='store')
    parser.add_argument('--author', action='store')
    args = parser.parse_args()
    return args


# This function returns all files with a given directory path
def list_all_files(dirName):
    all_files = list()
    for root, dirs, files in os.walk(dirName):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files


# intialize a .lgit folder-----------------
def init():
    if os.path.exists('.lgit'):
        if os.path.isdir('.lgit'):
            # print('Reinitialized existing Git repository in ' + lgit_path)
            print("Git repository already initialized.")
        elif os.path.isfile('.lgit'):
            print('fatal: Invalid gitfile format: ' + lgit_path)
    else:
        intial_git()
        # print("Initialized empty Git repository in " + lgit_path)


def intial_git():
    os.mkdir(lgit_path)
    os.mkdir(os.path.join(lgit_path, 'objects'))
    os.mkdir(os.path.join(lgit_path, 'commits'))
    os.mkdir(os.path.join(lgit_path, 'snapshots'))
    open('.lgit/index', 'wb').close()
    open('.lgit/config', 'a').close()
    #  write LOGNAME into config
    fd = os.open(os.path.join(lgit_path, 'config'), os.O_WRONLY)
    log_name = os.environ['LOGNAME']
    os.write(fd, log_name.encode())
    os.close(fd)


# this function returns a full .lgit path (even in a child dir)
def find_lgit_path():
    all_dirs = list()
    path = os.getcwd()
    while path != '/':
        dirs = os.listdir(path)
        if '.lgit' in dirs:
            return path + '/' + '.lgit'
        path = os.path.dirname(path)
    return path


# this function convert a string into SHA1----------
def convert_text_sha1(text):
    hash_object = hashlib.sha1(text.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


# copy file to lgit/objects/ ------sha1 (folder_name and file_name)
def copy_file_to_objects(filename):
    # open the file on the command line and get the content
    file_content = open(filename, 'r').read()
    # convert the file context into sha1
    sha1 = convert_text_sha1(file_content)
    dirname = sha1[:2]
    filename = sha1[2:]
    path_objects = find_lgit + '/objects/'
    if not os.path.exists(path_objects + dirname):
        os.mkdir(path_objects + dirname)
    # open filename(SHA1 code) and write the content
    file = open(path_objects + dirname + '/' + filename, 'w+')
    file.write(file_content)
    file.close()


# get_timestamp of a file
def get_timestamp(filename):
    # get modify time of a file
    utime = os.path.getmtime(filename)
    # change to timestamp
    result = datetime.datetime.fromtimestamp(utime)
    my_string = str(result)
    lst = list(my_string)
    em_str = ''
    for i in lst:
        if i != '-' and i != ' ' and i != ':':
            em_str += i
    return em_str


# get get_timestamp now
def get_now():
    second = time.time()
    timing = str(datetime.datetime.fromtimestamp(second))
    # process time -----> time stamp
    lstTime = [timing]
    get_time = ''
    for i in lstTime[0]:
        if i != '-' and i != ' ' and i != ':':
            get_time += i
    return get_time


# get file name file index-------------
def get_f_name_in_index():
    path_index = find_lgit + "/index"
    lst = convert_f_content_to_list(path_index)
    list_filename_index = []
    for i in lst:
        list_filename_index.append(i[0].split()[-1])
    return list_filename_index


def convert_f_content_to_list(filename):
    lst = []
    index = open(index_path)
    lines = index.readline()
    while lines != "":
        lst.append([lines.strip()])
        lines = index.readline()
    return lst


# write list to file
def write_to_file(filename, list):
    with open(filename, 'w') as f:
        for item in list:
            f.write("%s\n" % item[0])


# file_git_added, file_commited
def format_file_index(file_in_cwd):
    path_home = find_lgit_path()[:-5]
    file_write = file_in_cwd.replace(path_home, '')
    timestamp = get_timestamp(file_in_cwd)[:-7]
    # read file in current working direc
    content_cwd = open(file_in_cwd, 'r').read()
    sha1_cwd = convert_text_sha1(content_cwd)
    # get dirname and filename to locate the file in objects directory
    dirname = sha1_cwd[:2]
    filename = sha1_cwd[2:]
    content_objects = open(find_lgit + '/objects/' + dirname +
                           '/' + filename).read()
    sha1_obj = convert_text_sha1(content_objects)
    # check if the file_in_cwd commit or not
    # --------------------------sai----------------
    space = ' ' * 40
    if os.listdir(find_lgit + '/snapshots/') != []:
        name_f_in_snapshots = list_all_files(find_lgit + '/snapshots/')[0]
        content_f_snapshots = convert_f_content_to_list(name_f_in_snapshots)
        for i in content_f_snapshots:
            if file_in_cwd == i[0].split()[-1]:
                space = i[0].split()[0]
    return [timestamp + ' ' + sha1_cwd + ' ' + sha1_obj + ' ' +
            space + ' ' + file_write]


# this function adds files to objects dir and write to index
def process_add_command(list_item):
    for item in list_item:
        if os.path.isfile(item):
            copy_file_to_objects(item)
            _item_code = format_file_index(item)
            lst = check_exist_in_index(_item_code)
            write_to_file(index_path, lst)
        elif os.path.isdir(item):
            files = list_all_files(item)
            for file in files:
                copy_file_to_objects(file)
                _file_code = format_file_index(file)
                lst = check_exist_in_index(_file_code)
                write_to_file(index_path, lst)


def delete_content(filename):
    filename.seek(0)
    filename.truncate()


# check function checks if a file already exists in index_ ---> return a list
def check_exist_in_index(list):
    content_index = convert_f_content_to_list(index_path)
    flag = 0
    name = list[0].split()[-1]
    for i in range(len(content_index)):
        if content_index[i][0].split()[-1] == name:
            content_index[i] = list
            flag = 1
    if flag == 0:
        content_index.append(list)
    return content_index


def process_rm_command(list_file_to_remove):
    lst = convert_f_content_to_list(index_path)

    filename_index = get_f_name_in_index()
    path_home = find_lgit_path()[:-5]
    # get the filename in index --------> to remove afterwards
    f_name = []
    for i in filename_index:
        if i not in list_file_to_remove:
            f_name.append(i)
        else:
            os.remove(os.path.join(path_home, i))
    for i in range(len(lst)):
        lst[i] = lst[i][0].split(' ')
    result = []
    for i in range(len(lst)):
        if lst[i][-1] in f_name:
            text = ' '.join(lst[i])
            result.append([text])
    write_to_file(index_path, result)


def process_commit_command():
    get_time = get_now()
    file_in_commit = open(find_lgit + '/commits/' + get_time, 'w+')
    config = open(find_lgit + '/config', 'r')
    msg = config.read()
    config.close()
    file_in_commit.write(msg + '\n' + get_time[:-7] + '\n\n' +
                         str(message) + '\n\n')
    file_in_commit.close()
    # Empty snapshots_dir and create a new file after commiting
    if os.listdir(find_lgit + '/snapshots/') != []:
        name_f_in_snapshots = list_all_files(find_lgit + '/snapshots/')[0]
        os.remove(name_f_in_snapshots)
    file_in_snapshots = open(find_lgit + '/snapshots/' + get_time, 'w+')
    content_f_index = convert_f_content_to_list(index_path)
    # create a list sha1_name in folder objects to write to snapshots
    object_sha1 = []
    # save filename in snapshots
    filenames_in_snapshot = []
    for i in content_f_index:
        # sha1_obj + filename
        object_sha1.append(i[0].split()[1] + ' ' + i[0].split()[-1])
        filenames_in_snapshot.append(i[0].split()[-1])
    lst_rong = []
    for i in object_sha1:
        lst_rong.append([i])
    write_to_file(find_lgit + '/snapshots/' + get_time, lst_rong)
    # update file index
    get_content_index = convert_f_content_to_list(index_path)
    result = []
    # update to index -------------- :D
    for i in range(len(get_content_index)):
        get_content_index[i] = get_content_index[i][0].split()
        if len(get_content_index[i]) == 4:
            tem = get_content_index[i][3]
            get_content_index[i][3] = get_content_index[i][2]
            get_content_index[i].append(tem)
        elif len(get_content_index[i]) == 5:
            get_content_index[i][3] = get_content_index[i][2]
        rong = ''
        for j in get_content_index[i]:
            rong += j + ' '
        get_content_index[i] = rong[:-1]

    for i in get_content_index:
        result.append([i])
    write_to_file(index_path, result)


# --------------------------------------
def get_all_files():
    all_files = []
    list = os.listdir(find_lgit[:-5])
    for item in list:
        if os.path.isdir(os.path.join(find_lgit[:-5], item)):
            all_files.append(item + "/")
        else:
            all_files.append(item)
    if os.path.exists(find_lgit[:-5] + '/.lgit'):
        all_files.remove('.lgit/')
    return all_files


def find_changes():
    modified_files = []
    deleted_files = []
    f = open(index_path, 'r')
    f_content = f.read()
    lines = f_content.split('\n')
    for line in lines:
        if len(line) == 0:
            continue
        tracked_file = line.split()[-1]
        line_number = f_content.find(line)
        try:
            # if current working directory is not the directory of lgit:
            if os.getcwd() is not find_lgit_path()[:-5]:
                os.chdir(find_lgit_path()[:-5])
            # create sha1 and mtime of the current file:
            file_content = open(tracked_file, 'r').read()
            sha1_file = convert_text_sha1(file_content)
            file_mtime = get_timestamp(tracked_file)[:14] + " "
            # if sha1 of the current file is different from field 2,
            #  the file is modified
            if sha1_file != line.split()[1]:
                modified_files.append(tracked_file)
            file = os.open(index_path, os.O_RDWR)
            # update index file
            os.lseek(file, line_number, 0)
            os.write(file, file_mtime.encode())
            os.lseek(file, line_number + 15, 0)
            os.write(file, sha1_file.encode())
            os.close(file)
        except FileNotFoundError:
            deleted_files.append(tracked_file)
    return modified_files, deleted_files


def status():
    all_files = get_all_files()
    untracked_files = []
    tracked_files = get_f_name_in_index()
    modified_files, deleted_files = find_changes()
    not_staged = []
    to_be_committed = []
    new = []
    for file in all_files:
        if file not in tracked_files:
            untracked_files.append(file)
    f = open(index_path, 'r')
    lines = f.readlines()
    for line in lines:
        file_name = line.split()[-1]
        first_field = line[0:14]
        second_field = line[15:55]
        third_field = line[56:96]
        fourth_field = line[97:137]
        if second_field != third_field:
            not_staged.append(file_name)
        if third_field != fourth_field:
            to_be_committed.append(file_name)
        if fourth_field == ' ' * 40:
            new.append(file_name)
    print("On branch master\n\n")
    if len(os.listdir(commits_path)) == 0:
        print("No commits yet\n\n")
    if to_be_committed:
        print("Initial commit\n\n")

        print("Changes to be committed:\n  (use \033[93m \"./lgit.py reset "
              "HEAD ...\" \033[00m to unstage)\n")
        for file in to_be_committed:
            if file in new:
                print("\tnew file:   ", file)
            elif file in modified_files:
                print("\tmodified:   ", file)
            elif file in deleted_files:
                print("\tdeleted:   ", file)
    if not_staged:
        print("\nChanges not staged for commit:\n  (use \"./lgit.py ad "
              "...\" to update what will be committed)\n  "
              "(use \"./lgit.py checkout -- ...\" to discard "
              "changes in working directory)")
        for file in not_staged:
            if file in modified_files:
                print("\tmodified:   ", file)
            elif file in deleted_files:
                print("\tdeleted:   ", file)
    if untracked_files:
        untracked_files.sort()
        print("\n\nUntracked_files:\n  (use \"./lgit.py add <file>...\" to "
              "include \"Untracked files:\"\n")
        for file in untracked_files:
            print("\t", file)
    if not not_staged:
        print("\nno changes added to commit (use \"./lgit.py add "
              "and/or \"./lgit.py commit -a"")")


def log():
    list_commits = os.listdir(commits_path)
    if len(list_commits) == 0:
        print("fatal: your current branch 'master' does not "
              "have any commits yet")
        exit()
    # from new to old:
    list_commits.sort(reverse=True)
    for item in list_commits:
        commit = os.path.join(commits_path, item)
        f = open(commit, 'r')
        cont = f.read().split("\n")
        f.close()
        content = []
        #  remove "" in content
        for i in cont:
            if i != '':
                content.append(i)
        author = content[0]
        time_string = content[1]
        date = datetime.datetime.strptime(time_string, "%Y%m%d%H%M%S")
        # convert to human-readable date
        date = date.strftime("%a %b %d %H:%M:%S %Y")
        message = content[2]
        print("commit", item)
        print("Author: ", author)
        print("Date: ", date)
        print("\n\t", message, "\n\n")


def print_ls_files():
    path = os.getcwd()
    path1 = path + '/'
    path_home = find_lgit_path()[:-5]
    list_result = []
    files = list_all_files(path)
    fname_index = get_f_name_in_index()
    for f in range(len(files)):
        files[f] = files[f].replace(path_home, '')
    for i in files:
        if i in fname_index:
            list_result.append(i)
    list_result = sorted(list_result)
    for i in range(len(list_result)):
        list_result[i] = os.path.join(path_home, list_result[i])
    for i in range(len(list_result)):
        list_result[i] = list_result[i].replace(path1, '')
    # print ls-files -------------
    if list_result != []:
        print('\n'.join(list_result))
    else:
        exit()


def main():
    global lgit_path, index_path, path, commits_path, message, find_lgit
    path = os.getcwd()
    command = process_agruments().command
    message = process_agruments().message
    author = process_agruments().author
    lgit_path = os.path.abspath('.lgit')
    find_lgit = find_lgit_path()
    if find_lgit == '/':
        if command != ['init']:
            print('fatal: not a git repository (or any of '
                  'the parent directories)')
            exit()
    else:
        commits_path = os.path.join(find_lgit, 'commits')
        index_path = os.path.join(find_lgit, 'index')
    if command == ['init']:
        init()
    elif 'add' in command:
        # ----- copy file to .lgit/objects/
        lst_cmd = command[1:]
        fullpath = find_lgit_path()[:-5]
        for i in range(len(lst_cmd)):
            lst_cmd[i] = os.path.abspath(lst_cmd[i])
        for f in lst_cmd:
            if not os.path.isfile(f) and not os.path.isdir(f):
                print('fatal: not a git repository (or any of '
                      'the parent directories)')
                exit()
        process_add_command(lst_cmd)
    elif 'rm' in command:
        l_file_to_remove = command[1:]
        filename_index = get_f_name_in_index()
        fullpath = find_lgit_path()[:-5]
        for i in range(len(l_file_to_remove)):
            l_file_to_remove[i] = os.path.abspath(l_file_to_remove[i])
            l_file_to_remove[i] = l_file_to_remove[i].replace(fullpath, '')
        # print(l_file_to_remove)
        for i in l_file_to_remove:
            if i not in filename_index:
                print('fatal: pathspec ' + '\'' + i + '\'' + ' did not '
                      'match any files')
                exit()
        process_rm_command(l_file_to_remove)
    elif 'config' in command:
        f_config = open('.lgit/config', 'w+')
        f_config.write('%s\n' % (author))
        f_config.close()
    elif 'commit' in command:
        process_commit_command()
    elif "status" in command:
        status()
    elif "log" in command:
        log()
    elif 'ls-files' in command:
        if find_lgit == '/':
            exit()
        print_ls_files()


if __name__ == '__main__':
    main()
