cmake_minimum_required(VERSION 3.0)
project(nasm C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

set(COMPAT_SRC "")

include(CheckCSourceCompiles)
include(CheckFunctionExists)
include(CheckIncludeFile)
include(CheckSymbolExists)
include(CheckTypeSize)
include(TestBigEndian)

check_symbol_exists(__GNU_LIBRARY__ "features.h" _GNU_SOURCE)
if(_GNU_SOURCE)
    set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
    add_definitions(-D_GNU_SOURCE)
endif()

# Check large file support
include(LargeFiles)
test_large_files(_LARGE_FILES NO)

# Check if const is accepted
check_c_source_compiles("int main () {
#ifndef __cplusplus\n\
typedef int charset[2]; const charset cs = { 0, 0 };\n\
char const *const *pcpcc; char **ppc;\n\
struct point {int x, y;}; static struct point const zero = {0,0};\n\
const char *g = \"string\"; pcpcc = &g + (g ? g-g : 0);\n\
++pcpcc; ppc = (char**) pcpcc; pcpcc = (char const *const *) ppc;\n\
{ char tx; char *t = &tx; char const *s = 0 ? (char *) 0 : (char const *) 0; *t++ = 0; if (s) return 0; }\n\
{ int x[] = {25, 17}; const int *foo = &x[0]; ++foo; }\n\
{ typedef const int *iptr; iptr p = 0; ++p; }\n\
{ struct s { int j; const int *ap[3]; } bx; struct s *b = &bx; b->j = 5; }\n\
{ const int foo = 10; if (!foo) return 0; }\n\
return !cs[0] && !zero.x;\n\
#endif\n\
return 0; }" CONST_WORKING)
if(NOT CONST_WORKING)
    set(const 1)
endif()


# Check for inline keyword
set(inline 1)
foreach(KEYWORD inline;__inline__;__inline)
    check_c_source_compiles("#ifndef __cplusplus\n typedef int foo_t;\nstatic ${KEYWORD} foo_t static_foo () {return 0; }\n\
${KEYWORD} foo_t foo () {return 0; }\n#endif\n int main(){return 0;}" TEST_INLINE)
    if(TEST_INLINE)
        if("x${KEYWORD}" STREQUAL "xinline")
            set(inline 0)
        else()
            set(INLINE_KEYWORD ${KEYWORD})
        endif()
        break()
    endif()
endforeach()


# Check for restrict keyword
set(restrict 1)
foreach(KEYWORD __restrict __restrict__ _Restrict restrict)
    check_c_source_compiles("typedef int * int_ptr;	int foo (int_ptr ${KEYWORD} ip) { return ip[0]; } \
int main () { int s[1];	int * ${KEYWORD} t = s;	t[0] = 0; return foo(t); return 0;}" TEST_RESTRICT)
    if(TEST_RESTRICT)
        if("x${KEYWORD}" STREQUAL "xrestrict")
            set(restrict 0)
        else()
            set(RESTRICT_KEYWORD ${KEYWORD})
        endif()
        break()
    endif()
endforeach()

check_type_size(size_t HAVE_SIZE_T LANGUAGE C)
if(NOT HAVE_SIZE_T)
    set(size_t unsigned int)
endif()

check_c_source_compiles("#ifndef __cplusplus\n#include <stdbool.h>\n#endif\nint foo(bool x, int y){return x+y;} int main(){return 0;}" HAVE_WORKING_BOOL)

test_big_endian(WORDS_BIGENDIAN)
if(NOT WORDS_BIGENDIAN)
    set(WORDS_LITTLEENDIAN 1)
endif()

check_include_file(limits.h HAVE_LIMITS_H)
if(NOT HAVE_LIMITS_H)
    message(FATAL_ERROR "NASM requires '<limits.h>' to compile")
endif()

check_include_file(inttypes.h HAVE_INTTYPES_H)
check_include_file(strings.h HAVE_STRINGS_H)
check_include_file(stdbool.h HAVE_STDBOOL_H)
check_include_file(unistd.h HAVE_UNISTD_H)
check_include_file(sys/param.h HAVE_SYS_PARAM_H)

check_function_exists(strcspn HAVE_STRCSPN)
if(NOT HAVE_STRCSPN)
    message(FATAL_ERROR "NASM requires ANSI C (specifically, 'strcspn')")
endif()

check_function_exists(strspn HAVE_STRSPN)
if(NOT HAVE_STRCSPN)
    message(FATAL_ERROR "NASM requires ANSI C (specifically, 'strspn')")
endif()


check_symbol_exists(vsnprintf stdio.h HAVE_VSNPRINTF)
check_symbol_exists(_vsnprintf stdio.h HAVE__VSNPRINTF)
if(NOT HAVE_VSNPRINTF AND NOT HAVE__VSNPRINTF)
    set(COMPAT_SRC ${COMPAT_SRC} lib/vsnprintf.c)
endif()

check_symbol_exists(snprintf stdio.h HAVE_SNPRINTF)
check_symbol_exists(_snprintf stdio.h HAVE__SNPRINTF)
if(NOT HAVE_SNPRINTF AND NOT HAVE__SNPRINTF)
    set(COMPAT_SRC ${COMPAT_SRC} lib/snprintf.c)
endif()

check_symbol_exists(strcasecmp "strings.h" HAVE_DECL_STRCASECMP)
set(HAVE_STRCASECMP ${HAVE_DECL_STRCASECMP})

check_symbol_exists(stricmp "string.h" HAVE_DECL_STRICMP)
set(HAVE_STRICMP ${HAVE_DECL_STRICMP})

check_symbol_exists(strlcpy "string.h" HAVE_DECL_STRLCPY)
set(HAVE_STRLCPY ${HAVE_DECL_STRLCPY})

check_symbol_exists(strncasecmp "strings.h" HAVE_DECL_STRNCASECMP)
set(HAVE_STRNCASECMP ${HAVE_DECL_STRNCASECMP})

check_symbol_exists(strnicmp "string.h" HAVE_DECL_STRNICMP)
set(HAVE_STRNICMP ${HAVE_DECL_STRNICMP})

check_symbol_exists(strsep "string.h" HAVE_DECL_STRSEP)
set(HAVE_STRSEP ${HAVE_DECL_STRSEP})

set(CMAKE_REQUIRED_INCLUDES unistd.h stdlib.h)
check_function_exists(getuid HAVE_GETUID)
check_function_exists(getgid HAVE_GETGID)

check_function_exists(realpath HAVE_REALPATH)
check_function_exists(canonicalize_file_name HAVE_CANONICALIZE_FILE_NAME)
check_function_exists(_fullpath HAVE__FULLPATH)
check_function_exists(pathconf HAVE_PATHCONF)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/config.h.cmake ${CMAKE_CURRENT_BINARY_DIR}/config.h)

add_definitions(-DHAVE_CONFIG_H)
include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})
if(NOT HAVE_INTTYPES_H)
    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/inttypes)
endif()

add_library(nasmlib OBJECT nasmlib.c)

add_executable(nasm nasm.c ver.c raa.c saa.c rbtree.c srcfile.c realpath.c float.c insnsa.c insnsb.c directiv.c
    assemble.c labels.c hashtbl.c crc64.c parser.c output/outform.c output/outlib.c output/nulldbg.c output/nullout.c
    output/outbin.c output/outaout.c output/outcoff.c output/outelf.c output/outelf32.c output/outelf64.c
    output/outelfx32.c output/outobj.c output/outas86.c output/outrdf2.c output/outdbg.c output/outieee.c
    output/outmacho.c md5c.c output/codeview.c preproc.c quote.c pptok.c macros.c listing.c eval.c exprlib.c stdscan.c
    strfunc.c tokhash.c regvals.c regflags.c ilog2.c lib/strlcpy.c preproc-nop.c disp8.c iflag.c
    $<TARGET_OBJECTS:nasmlib> ${COMPAT_SRC})
    
add_executable(ndisasm ndisasm.c disasm.c sync.c $<TARGET_OBJECTS:nasmlib> ver.c insnsd.c insnsb.c insnsn.c regs.c
    regdis.c disp8.c iflag.c)

#rdoff
add_library(ldrdflibs OBJECT rdoff/rdoff.c rdoff/symtab.c rdoff/collectn.c rdoff/rdlib.c rdoff/segtab.c rdoff/hash.c)
add_library(rdxlibs OBJECT rdoff/rdoff.c rdoff/rdfload.c rdoff/symtab.c rdoff/collectn.c rdoff/hash.c)
add_executable(rdfdump rdoff/rdfdump.c rdoff/rdoff.c)
add_executable(ldrdf rdoff/ldrdf.c $<TARGET_OBJECTS:ldrdflibs> $<TARGET_OBJECTS:nasmlib>)
add_executable(rdx rdoff/rdx.c $<TARGET_OBJECTS:rdxlibs> $<TARGET_OBJECTS:nasmlib>)
add_executable(rdflib rdoff/rdflib.c)
add_executable(rdf2bin rdoff/rdf2bin.c $<TARGET_OBJECTS:rdxlibs> $<TARGET_OBJECTS:nasmlib>)