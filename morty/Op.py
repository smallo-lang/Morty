class Op:
    """ Op contains Rick's opcodes and their byte representations. """
    END  = b'\x00'
    PUSH = b'\x01'
    POP  = b'\x02'
    DROP = b'\x03'
    INI  = b'\x04'
    INS  = b'\x05'
    OUT  = b'\x06'
    NL   = b'\x07'
    STI  = b'\x08'
    BOOL = b'\x09'
    ADD  = b'\x0A'
    SUB  = b'\x0B'
    MUL  = b'\x0C'
    DIV  = b'\x0D'
    MOD  = b'\x0E'
    GTH  = b'\x0F'
    LTH  = b'\x10'
    GEQ  = b'\x11'
    LEQ  = b'\x12'
    NOT  = b'\x13'
    AND  = b'\x14'
    OR   = b'\x15'
    EQ   = b'\x16'
    NEQ  = b'\x17'
    CON  = b'\x18'
    JUMP = b'\x19'
    JMPT = b'\x1A'
    JMPF = b'\x1B'
    BR   = b'\x1C'
    BRT  = b'\x1D'
    BRF  = b'\x1E'
    BACK = b'\x1F'
    ERR  = b'\x20'