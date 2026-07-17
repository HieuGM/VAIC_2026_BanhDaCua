package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.ProcedureDto;
import com.hanoiheart.dataapi.entity.Procedure;
import com.hanoiheart.dataapi.repository.ProcedureRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ProcedureService {

    private final ProcedureRepository repository;

    public ProcedureService(ProcedureRepository repository) {
        this.repository = repository;
    }

    public List<ProcedureDto> list(String code) {
        List<Procedure> rows = (code == null || code.isBlank())
                ? repository.findAllByOrderByCodeAscStepNoAsc()
                : repository.findByCodeOrderByStepNoAsc(code);
        return rows.stream().map(this::toDto).toList();
    }

    private ProcedureDto toDto(Procedure p) {
        return new ProcedureDto(p.getId(), p.getCode(), p.getTitle(), p.getStepNo(),
                p.getName(), p.getDescription(), p.getResponsibleRole(),
                p.getRelatedForm(), p.getSourceDoc());
    }
}
