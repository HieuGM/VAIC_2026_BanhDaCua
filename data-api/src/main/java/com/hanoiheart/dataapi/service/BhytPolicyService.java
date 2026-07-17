package com.hanoiheart.dataapi.service;

import com.hanoiheart.dataapi.dto.BhytPolicyDto;
import com.hanoiheart.dataapi.entity.BhytPolicy;
import com.hanoiheart.dataapi.repository.BhytPolicyRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BhytPolicyService {

    private final BhytPolicyRepository repository;

    public BhytPolicyService(BhytPolicyRepository repository) {
        this.repository = repository;
    }

    public List<BhytPolicyDto> list(String category) {
        List<BhytPolicy> rows = (category == null || category.isBlank())
                ? repository.findAllByOrderByCategoryAscCodeAsc()
                : repository.findByCategoryOrderByCode(category);
        return rows.stream().map(this::toDto).toList();
    }

    private BhytPolicyDto toDto(BhytPolicy p) {
        return new BhytPolicyDto(p.getId(), p.getCode(), p.getTitle(), p.getCategory(),
                p.getSummary(), p.getDetailsMd(), p.getSourceUrl(), p.getEffectiveDate());
    }
}
