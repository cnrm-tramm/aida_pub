extern int errapt;

char *
strerrapt (int errnum);

void
perrapt (const char *s);

/** RAPT error code for no RAPT-specific system error, documented by errno */
#define RAPT_ERRNO       1

/** RAPT error code for invalid argument */
#define RAPT_EINVAL      2

/** RAPT error code for bad file descriptor */
#define RAPT_EBADF       3

/** RAPT error code for failed open : precise error code in errno */
#define RAPT_EOPEN       4

/** RAPT error code for failed read : precise error code in errno */
#define RAPT_EREAD       5

/** RAPT error code for failed write : precise error in errno */
#define RAPT_EWRITE      6

/** RAPT error code for failed memory allocation : precise error code in errno */
#define RAPT_ENOMEM      7

/** RAPT error code for failed memory mapping : precise error code in errno */
#define RAPT_EMMAP       8

/** RAPT error code for generic file format error */
#define RAPT_EFFORMAT    9

/** RAPT error code for file format error : bad start*/
#define RAPT_EFFMT_START    10

/** RAPT error code for file format error : negative header len */
#define RAPT_EFFMT_HLEN_NEG    11

/** RAPT error code for file format error : no \n after head_len */
#define RAPT_EFFMT_HLEN_SEP    12

/** RAPT error code for file format error : missing "FIN_HDR" */
#define RAPT_EFFMT_HDR_END    13

/** RAPT error code for file positioning error */
#define RAPT_ENOPOS     14

/** RAPT error code for bad Acq_Id length (!= 6 OR 8) */
#define RAPT_EBADID     15

/** RAPT error code for unrecognised platform. */
#define RAPT_EBADACFT   16

/** RAPT error code for unrecognised data format */
#define RAPT_EBADFMT    17

/** RAPT error code for bad year substring in Acq_ID */
#define RAPT_EBADYSTR   18

/** RAPT error code for bad NumAcq substring in Acq_ID */
#define RAPT_EBADNSTR   19

/** RAPT error code for bad NumAcq substring in Acq_ID */
#define RAPT_ENEGFREQ   20

/** RAPT error code for invalid Aida_Typ_Code */
#define RAPT_EBADATYC   21

/** RAPT error code for a vector which doesn't match requested name */
#define RAPT_EBADVECNAM 22

/** RAPT error code for  Not a regular file */
#define RAPT_ENOTAFILE  23

/** RAPT error code for trying to work on somebody else's file */
#define RAPT_ENOTYOURS  24

/** RAPT error code when missing read permission */
#define RAPT_ENOREAD    25

/** RAPT error code when missing write permission */
#define RAPT_ENOWRITE   26

/** RAPT error code when unable to determine endianness of machine */
#define RAPT_EBADEND    27

/** RAPT error code for too short given path string */
#define RAPT_SHORTPATH    28

/** RAPT error code for file format error : too short */
#define RAPT_EFFMT_SHORT    29

